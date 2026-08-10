from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Driver

@api_view(['POST'])
@permission_classes([AllowAny])
def update_trip_status(request):
    try:
        trip_id = request.data.get('trip_id')
        is_ready = request.data.get('is_ready') in [True, 'true', 'True']
        is_coming = request.data.get('is_coming') in [True, 'true', 'True']
        is_rejected = request.data.get('is_rejected') in [True, 'true', 'True']
        
        if not trip_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required field (trip_id).",
                "body": {}
            }, status=400)
            
        if is_ready:
            driver_status = 'ready'
        elif is_coming:
            driver_status = 'coming'
        elif is_rejected:
            driver_status = 'rejected'
        else:
            return Response({
                "code": 400,
                "status": False,
                "message": "You must provide either 'is_ready': true, 'is_coming': true, or 'is_rejected': true.",
                "body": {}
            }, status=400)
            
        trip = Trip.objects.filter(trip_id=trip_id).first()
        booking = None
        if not trip:
            from sevy_app.models import CarBooking
            booking = CarBooking.objects.filter(booking_id=trip_id).first()
            if not booking:
                return Response({
                    "code": 404,
                    "status": False,
                    "message": "Trip or Booking not found.",
                    "body": {}
                }, status=404)
                
        # --- CAR BOOKING LOGIC ---
        if booking:
            driver = booking.driver
            if not driver:
                return Response({
                    "code": 400,
                    "status": False,
                    "message": "This booking does not have an assigned driver.",
                    "body": {}
                }, status=400)
                
            if is_ready:
                booking.driver_status = 'accepted'
                driver.is_available = False
                driver.save()
                
                # Auto-completion celery task removed; now done manually                    
            elif is_rejected:
                booking.driver_status = 'rejected'
                driver.is_available = True
                driver.save()
                
                # Reassign logic
                from django.utils import timezone
                from sevy_app.tasks import booking_timeout_task
                from sevy_app.models import CarBooking
                
                new_driver = Driver.objects.filter(userid__custom_id="5321694aa6cc751b55959f8b").first()
                if new_driver:
                    booking.driver = new_driver
                    booking.driver_status = 'waiting'
                    booking.status = 'pending'
                    try:
                        booking.save()
                        CarBooking.objects.filter(pk=booking.pk).update(created_at=timezone.now())
                        booking_timeout_task.apply_async((booking.booking_id,), countdown=1800)
                    except Exception as celery_err:
                        print(f"Failed to schedule celery task: {celery_err}")
                        
                    from sevy_app.models import Notification
                    Notification.objects.create(
                        user=new_driver.userid,
                        title="New Booking Request",
                        message="You have a new car rental booking request.",
                        notification_type='driverbooking',
                        related_id=booking.booking_id
                    )

            booking.save()
            
            # Customer Notification
            from sevy_app.models import Notification
            from sevy_app.utils.fcm_service import send_fcm_notification
            if is_rejected:
                Notification.objects.create(
                    user=booking.user,
                    title="Booking Request Rejected",
                    message=f"Your driver {driver.full_name} has rejected your rental request.",
                    notification_type='rental',
                    related_id=booking.booking_id
                )
                send_fcm_notification(
                    user=booking.user,
                    title="Booking Request Rejected",
                    body="Your assigned driver rejected the booking. We have assigned another driver to you.",
                    data={"type": "rental", "booking_id": str(booking.booking_id)}
                )
            elif is_ready:
                Notification.objects.create(
                    user=booking.user,
                    title="Driver Accepted",
                    message=f"Your driver {driver.full_name} has accepted your rental request.",
                    notification_type='rental',
                    related_id=booking.booking_id
                )
                send_fcm_notification(
                    user=booking.user,
                    title="Driver Accepted",
                    body="Your assigned driver has accepted the rental booking.",
                    data={"type": "rental", "booking_id": str(booking.booking_id)}
                )
                
            return Response({
                "code": 200,
                "status": True,
                "message": f"Booking driver status updated.",
                "body": {
                    "trip_id": booking.booking_id,
                    "driver_status": booking.driver_status
                }
            }, status=200)

        # --- NORMAL TRIP LOGIC (CONTINUES HERE) ---
        driver = trip.driverid
        if not driver:
            return Response({
                "code": 400,
                "status": False,
                "message": "This trip does not have an assigned driver.",
                "body": {}
            }, status=400)
            
        trip.driver_status = driver_status
        if driver_status == 'coming':
            trip.status = 'active'
        if driver_status == 'ready':
            from django.utils import timezone
            from datetime import timedelta
            
            driver.is_available = False
            driver.save()
            trip.created_at = timezone.now()
            trip.save()
            
            if getattr(trip, 'trip_type', 'instanttrip') == 'scheduledtrip':
                # SCHEDULED TRIP: Do not trigger auto-cancel timeout.
                # Just schedule the 60m, 30m, 10m reminders.
                from sevy_app.tasks import scheduled_trip_reminder_task
                try:
                    for mins in [60, 30, 10]:
                        reminder_time = trip.start_time - timedelta(minutes=mins)
                        if reminder_time > timezone.now():
                            scheduled_trip_reminder_task.apply_async((trip.trip_id, mins), eta=reminder_time)
                    print(f"Scheduled 60m, 30m, 10m reminders for scheduled trip {trip.trip_id}")
                except Exception as celery_err:
                    print(f"Failed to schedule celery task: {celery_err}")
            else:
                # INSTANT TRIP: Start the 15-minute countdown for the driver to start driving
                from sevy_app.tasks import trip_timeout_task
                try:
                    print(f"\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Driver {driver.full_name} accepted Trip {trip.trip_id}. Starting 15-minute 'ready' countdown.")
                    print(f":::::::::::::::::::::::::::::::\n")
                    trip_timeout_task.apply_async((trip.trip_id, 'ready'), countdown=900)
                except Exception as celery_err:
                    print(f"Failed to schedule celery task: {celery_err}")
                
        if driver_status == 'rejected':
            from django.utils import timezone
            from sevy_app.tasks import trip_timeout_task
            
            driver.is_available = True
            driver.save()
            
            # MOCK: Assign new driver
            new_driver = Driver.objects.filter(userid__custom_id="5321694aa6cc751b55959f8b").first()
            if new_driver:
                trip.driverid = new_driver
                driver_status = 'waiting' # Reset to waiting for the new driver
                trip.driver_status = 'waiting'
                trip.status = 'upcoming'
                trip.created_at = timezone.now()
                
                try:
                    trip_timeout_task.apply_async((trip.trip_id, 'waiting'), countdown=1800)
                except Exception as celery_err:
                    print(f"Failed to schedule celery task: {celery_err}")
                    
                # Notify new driver
                from sevy_app.models import Notification
                Notification.objects.create(
                    user=new_driver.userid,
                    title="New Trip Request",
                    message=f"You have a new trip request from {trip.start_place_name} to {trip.destination_name}.",
                    notification_type='drivertrip',
                    related_id=trip.trip_id
                )

        trip.save()
        
        # Create a notification for the customer only if not silently reassigning
        from sevy_app.models import Notification
        from sevy_app.utils.fcm_service import send_fcm_notification
        
        if is_rejected:
            status_msg = "has rejected"
            title = "Trip Request Rejected"
            Notification.objects.create(
                user=trip.userid,
                title=title,
                message=f"Your driver {driver.full_name} {status_msg} your trip request.",
                notification_type='trip',
                related_id=trip.trip_id
            )
            send_fcm_notification(
                user=trip.userid,
                title=title,
                body="Driver cancelled the trip. We are looking for another driver for you.",
                data={"type": "trip", "trip_id": str(trip.trip_id)}
            )
            from sevy_app.utils.notifications import notify_admins
            notify_admins(
                title="Trip Rejected by Driver",
                message=f"Driver {driver.full_name} rejected trip {trip.tracking_number or trip.trip_id}.",
                notification_type="trip_cancelled",
                related_id=trip.trip_id
            )
        elif is_ready:
            status_msg = "is getting ready for"
            title = "Driver is Ready"
            Notification.objects.create(
                user=trip.userid,
                title=title,
                message=f"Your driver {driver.full_name} {status_msg} your trip request.",
                notification_type='trip',
                related_id=trip.trip_id
            )
        elif is_coming:
            status_msg = "is on the way for"
            title = "Driver is Coming"
            Notification.objects.create(
                user=trip.userid,
                title=title,
                message=f"Your driver {driver.full_name} {status_msg} your trip request.",
                notification_type='trip',
                related_id=trip.trip_id
            )
            send_fcm_notification(
                user=trip.userid,
                title=title,
                body=f"The driver is on their way. Expect them to arrive in {trip.estimated_time} (Distance: {trip.trip_distance_km} km).",
                data={"type": "trip", "trip_id": str(trip.trip_id)}
            )
        
        return Response({
            "code": 200,
            "status": True,
            "message": f"Trip driver status updated to {driver_status}.",
            "body": {
                "trip_id": trip.trip_id,
                "driver_status": trip.driver_status
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
