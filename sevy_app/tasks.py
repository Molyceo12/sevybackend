from celery import shared_task
from sevy_app.models import Trip, Driver

@shared_task
def trip_timeout_task(trip_id, expected_status='waiting'):
    try:
        trip = Trip.objects.get(trip_id=trip_id)
        
        # If the driver successfully advanced to the next state, this timeout is obsolete!
        if trip.driver_status != expected_status:
            print(f"\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print(f"Task Ignored: Trip {trip_id} timeout ended for '{expected_status}', but driver is already '{trip.driver_status}'.")
            print(f":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
            return
            
        print(f"\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(f"trip : {trip_id} , timeout ended for status: {expected_status}. Driver failed to advance.")
        print(f":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        
        current_driver = trip.driverid
        
        # Free up the old driver who missed the request
        if current_driver:
            current_driver.is_available = True
            current_driver.save()
            
            # Send notification to the old driver
            from sevy_app.models import Notification
            Notification.objects.create(
                user=current_driver.userid,
                title="Trip Missed",
                message=f"You missed a trip request from {trip.start_place_name} to {trip.destination_name} because you did not respond in time. It has been reassigned.",
                notification_type='drivertrip',
                related_id=trip.trip_id
            )
            
            from sevy_app.utils.fcm_service import send_fcm_notification
            send_fcm_notification(
                user=current_driver.userid,
                title="Trip Missed",
                body=f"You missed a trip request from {trip.start_place_name} to {trip.destination_name} because you did not respond in time.",
                data={"type": "drivertripmissed", "trip_id": str(trip.trip_id)}
            )
            
            send_fcm_notification(
                user=trip.userid,
                title="Driver Timeout",
                body="Driver did not respond in time. We are looking for another driver for you.",
                data={"type": "trip", "trip_id": str(trip.trip_id)}
            )
        
        # MOCK: Always assign this specific test driver to match the API
        new_driver = Driver.objects.filter(userid__custom_id="1a53c42d5499a1aad141d585").first()
        
        if new_driver:
            from django.utils import timezone
            now = timezone.now()
            trip.driverid = new_driver
            trip.driver_status = 'waiting' # Reset back to the beginning of the cycle
            trip.status = 'upcoming'
            trip.save()
            
            # Use .update() to bypass Django's auto_now_add protection for created_at
            Trip.objects.filter(pk=trip.pk).update(created_at=now)
            print(f"Re-assigned trip {trip_id} to new driver {new_driver.full_name}")
            
            from sevy_app.models import Notification
            from sevy_app.utils.fcm_service import send_fcm_notification
            
            # Notify new driver
            Notification.objects.create(
                user=new_driver.userid,
                title="New Trip Request",
                message=f"You have a new trip request from {trip.start_place_name} to {trip.destination_name}.",
                notification_type='drivertrip',
                related_id=trip.trip_id
            )
            
            send_fcm_notification(
                user=new_driver.userid,
                title="New Trip Request",
                body=f"You have a new trip request from {trip.start_place_name} to {trip.destination_name}.",
                data={"type": "trip", "trip_id": str(trip.trip_id)}
            )
            
            # Notify customer of successful reassignment
            send_fcm_notification(
                user=trip.userid,
                title="Trip Reassigned",
                body=f"Good news! Your trip has been reassigned to a new driver: {new_driver.full_name}.",
                data={"type": "trip", "trip_id": str(trip.trip_id)}
            )
            
            # Schedule a new 8-minute timeout for the new driver
            trip_timeout_task.apply_async((trip.trip_id, 'waiting'), countdown=480)
        else:
            print(f"No new driver available for trip {trip_id}. Trip remains or can be cancelled.")
                
    except Trip.DoesNotExist:
        print(f"trip : {trip_id} , timeout ended (Trip not found)")

@shared_task
def mark_car_unavailable_task(car_id):
    from sevy_app.models import Car
    try:
        car = Car.objects.get(car_id=car_id)
        car.status = 'booked'
        car.save()
        print(f"Car {car.brand} {car.name} marked as booked.")
    except Car.DoesNotExist:
        pass

@shared_task
def mark_car_available_task(car_id):
    from sevy_app.models import Car
    try:
        car = Car.objects.get(car_id=car_id)
        car.status = 'available'
        car.save()
        print(f"Car {car.brand} {car.name} marked as available.")
    except Car.DoesNotExist:
        pass

@shared_task
def booking_timeout_task(booking_id):
    from sevy_app.models import CarBooking
    try:
        booking = CarBooking.objects.get(booking_id=booking_id)
        if booking.driver_status != 'waiting':
            print(f"Booking {booking_id} was already acted upon or has no driver.")
            return
            
        print(f"Booking {booking_id} driver timeout. Reassigning...")
        
        # Free up the old driver if needed
        if booking.driver:
            booking.driver.is_available = True
            booking.driver.save()
            
            # Send notification to the old driver
            from sevy_app.models import Notification
            Notification.objects.create(
                user=booking.driver.userid,
                title="Booking Missed",
                message=f"You missed a car rental booking request because you did not respond in time.",
                notification_type='driverbooking',
                related_id=booking.booking_id
            )
            
            from sevy_app.utils.fcm_service import send_fcm_notification
            car_image = booking.car.images[0] if booking.car and booking.car.images else None
            send_fcm_notification(
                user=booking.user,
                title="Booking Driver Timeout",
                body="Your assigned driver did not respond in time. We have assigned another driver to you.",
                data={"type": "rental", "booking_id": str(booking.booking_id)},
                image=car_image
            )
            
            # Notify the company
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Driver Missed Booking",
                    message=f"Driver {booking.driver.full_name} failed to respond to the assignment for your {booking.car.brand} {booking.car.name}. We are reassigning a new driver.",
                    notification_type="companybooking",
                    related_id=booking.booking_id
                )
                send_fcm_notification(
                    user=company_user,
                    title="Driver Missed Booking",
                    body=f"Driver {booking.driver.full_name} failed to respond to the assignment. We are reassigning a new driver.",
                    data={"type": "companybooking", "booking_id": str(booking.booking_id)},
                    image=car_image
                )
            
        # MOCK: Always assign this specific test driver to match the API
        from sevy_app.models import Driver
        new_driver = Driver.objects.filter(userid__custom_id="1a53c42d5499a1aad141d585").first()
        
        if new_driver:
            from django.utils import timezone
            now = timezone.now()
            booking.driver = new_driver
            booking.status = 'pending'
            booking.driver_status = 'waiting'
            booking.save()
            
            # Use .update() to bypass Django's auto_now_add protection for created_at
            from sevy_app.models import CarBooking
            CarBooking.objects.filter(pk=booking.pk).update(created_at=now)
            print(f"Re-assigned booking {booking_id} to new driver {new_driver.full_name}")
            
            # Schedule a new 8-minute timeout for the new driver
            booking_timeout_task.apply_async((booking.booking_id,), countdown=480)
        else:
            booking.status = 'cancelled'
            booking.driver_status = None
            booking.save()
            print(f"No new driver available for booking {booking_id}. Cancelled.")
            
    except CarBooking.DoesNotExist:
        pass

@shared_task
def complete_booking_task(booking_id):
    from sevy_app.models import CarBooking, Notification
    from sevy_app.utils.notifications import notify_admins
    try:
        booking = CarBooking.objects.get(booking_id=booking_id)
        
        # Only complete it if it hasn't been cancelled
        if booking.status != 'cancelled' and booking.status != 'completed':
            booking.status = 'completed'
            booking.driver_status = None # Clear driver status when completed
            
            if booking.driver:
                booking.driver.is_available = True
                booking.driver.save()
                
                Notification.objects.create(
                    user=booking.driver.userid,
                    title="Rental Completed",
                    message="Your car rental booking has ended. You are now available for new requests.",
                    notification_type='driverbooking',
                    related_id=booking.booking_id
                )
                
            if booking.car:
                booking.car.status = 'available'
                booking.car.save()
                
            booking.save()
            

            
            # Notify the company
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Booking Completed",
                    message=f"The rental booking for your {booking.car.brand} {booking.car.name} has ended automatically.",
                    notification_type="rental",
                    related_id=booking.booking_id
                )
                
            # Notify Admins
            notify_admins(
                title="Booking Completion Request",
                message=f"A completion request for booking {getattr(booking, 'booking_number', None) or booking.booking_id} requires your review and approval. (Auto-completed by system)",
                notification_type="transaction",
                related_id=booking.booking_id
            )
                
            print(f"Automatically completed booking {booking_id} at its end_date.")
            
    except CarBooking.DoesNotExist:
        pass

@shared_task
def auto_accept_trip_completion_task(trip_id):
    from sevy_app.models import Trip, Notification
    try:
        trip = Trip.objects.get(trip_id=trip_id)
        if trip.approval_status == 'requestsent':
            trip.status = 'completed'
            trip.approval_status = 'approved'
            trip.save()
            
            if trip.driverid and trip.driverid.userid:
                Notification.objects.create(
                    user=trip.driverid.userid,
                    title="Trip Confirmed Automatically",
                    message=f"The completion of trip {trip.tracking_number or trip.trip_id} was automatically accepted.",
                    notification_type='drivertrip',
                    related_id=trip.trip_id
                )
                
                from sevy_app.utils.fcm_service import send_fcm_notification
                send_fcm_notification(
                    user=trip.driverid.userid,
                    title="Trip Confirmed Automatically",
                    body=f"The completion of trip {trip.tracking_number or trip.trip_id} was automatically accepted.",
                    data={"type": "drivertrip", "trip_id": str(trip.trip_id)}
                )
                
            # Notify Admins
            from sevy_app.utils.notifications import notify_admins
            tx_type = "company_transaction" if (trip.driverid and trip.driverid.companyid) else "driver_transaction"
            try:
                notify_admins(
                    title="Trip Completion Request",
                    message=f"A completion request for trip {trip.tracking_number or trip.trip_id} requires your review and approval. (Auto-accepted by system)",
                    notification_type=tx_type,
                    related_id=trip.trip_id
                )
            except Exception as e:
                print(f"\\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                print(f"Auto Trip Completion Notification Error:\\n{str(e)}")
                print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\\n")
                
            print(f"Automatically accepted completion request for trip {trip_id}")
    except Trip.DoesNotExist:
        pass

@shared_task
def auto_approve_booking_completion_task(booking_id):
    from sevy_app.models import CarBooking, Notification
    from sevy_app.utils.fcm_service import send_fcm_notification
    from sevy_app.utils.email_service import send_notification_email

    try:
        booking = CarBooking.objects.get(booking_id=booking_id)
        if booking.customer_approval_status == 'requestsent':
            # Approve it
            booking.customer_approval_status = 'approved'
            booking.save()
            
            # Find the company user
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            notification_title = "Booking Completed Automatically"
            notification_msg = f"The completion of your booking for {booking.car.brand} {booking.car.name} was automatically accepted by the system."

            # Notify Customer
            if booking.user:
                Notification.objects.create(
                    user=booking.user,
                    title=notification_title,
                    message=notification_msg,
                    notification_type='rental',
                    related_id=booking.booking_id
                )
                
                send_fcm_notification(
                    user=booking.user,
                    title=notification_title,
                    body=notification_msg,
                    data={"type": "rental", "booking_id": str(booking.booking_id)}
                )
                
                if booking.user.email:
                    send_notification_email(
                        to_email=booking.user.email,
                        subject=notification_title,
                        name=booking.user.full_names if hasattr(booking.user, 'full_names') else "Customer",
                        message="Your car rental booking completion has been automatically approved by the system. Thank you for using Sevy!",
                        details=[
                            {"label": "Booking ID", "value": booking.booking_number or booking.booking_id},
                            {"label": "Car", "value": f"{booking.car.brand} {booking.car.name}"},
                        ]
                    )

            # Notify Company
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title=notification_title,
                    message=f"The completion of the booking for your {booking.car.brand} {booking.car.name} was automatically accepted.",
                    notification_type='companybooking',
                    related_id=booking.booking_id
                )
                
                send_fcm_notification(
                    user=company_user,
                    title=notification_title,
                    body=f"The completion of the booking for your {booking.car.brand} {booking.car.name} was automatically accepted.",
                    data={"type": "companybooking", "booking_id": str(booking.booking_id)}
                )
                
                if company_user.email:
                    send_notification_email(
                        to_email=company_user.email,
                        subject=notification_title,
                        name=company_user.full_names if hasattr(company_user, 'full_names') else "Company",
                        message="A customer's car rental booking completion has been automatically approved by the system.",
                        details=[
                            {"label": "Booking ID", "value": booking.booking_number or booking.booking_id},
                            {"label": "Car", "value": f"{booking.car.brand} {booking.car.name}"},
                        ]
                    )
                
            print(f"Automatically accepted completion request for booking {booking_id}")
    except CarBooking.DoesNotExist:
        pass

@shared_task
def send_fcm_notification_task(user_id, title, body, data=None, image=None):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        from sevy_app.utils.fcm_service import _execute_send_fcm_notification
        _execute_send_fcm_notification(user, title, body, data, image)
    except User.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error in send_fcm_notification_task: {str(e)}")

@shared_task
def send_email_task(to_email, subject, template_name, context_data):
    try:
        from sevy_app.utils.email_service import _execute_send_customer_email
        _execute_send_customer_email(to_email, subject, template_name, context_data)
    except Exception as e:
        print(f"Error in send_email_task: {str(e)}")
