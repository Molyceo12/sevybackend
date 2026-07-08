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
                notification_type='trip',
                related_id=trip.trip_id
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
            
            # Schedule a new 2-minute timeout for the new driver
            trip_timeout_task.apply_async((trip.trip_id, 'waiting'), countdown=120)
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
                notification_type='rental',
                related_id=booking.booking_id
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
                    notification_type="rental",
                    related_id=booking.booking_id
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
            
            # Schedule a new 2-minute timeout for the new driver
            booking_timeout_task.apply_async((booking.booking_id,), countdown=120)
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
                    notification_type='rental',
                    related_id=booking.booking_id
                )
                
            if booking.car:
                booking.car.status = 'available'
                booking.car.save()
                
            booking.save()
            
            # Notify admins of completion
            notify_admins(
                title="Rental Booking Completed",
                message=f"Rental booking {booking.booking_id} has automatically completed as scheduled.",
                notification_type="rental",
                related_id=booking.booking_id
            )
            
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
                    message=f"The customer did not respond within 24 hours, so the completion of trip {trip.tracking_number or trip.trip_id} was automatically accepted.",
                    notification_type='trip_approval',
                    related_id=trip.trip_id
                )
                
            print(f"Automatically accepted completion request for trip {trip_id}")
    except Trip.DoesNotExist:
        pass
