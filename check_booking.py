import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy_backend.settings')
django.setup()

from sevy_app.models import CarBooking

booking_id = "c0ce5b87b5e0dbb6d60496a1"
try:
    booking = CarBooking.objects.get(booking_id=booking_id)
    print(f"Found Booking: {booking.booking_id}")
    print(f"Status: {booking.status}")
    print(f"Company ID: {booking.companyid_id}")
    
    has_user = False
    try:
        has_user = booking.user is not None
    except Exception as e:
        print(f"User error: {e}")
        
    has_car = False
    try:
        has_car = booking.car is not None
    except Exception as e:
        print(f"Car error: {e}")

    print(f"Has User: {has_user}")
    print(f"Has Car: {has_car}")
    
    # Test what select_related returns
    qs = CarBooking.objects.select_related('user', 'car', 'driver', 'transaction').filter(booking_id=booking_id)
    print(f"In select_related query: {qs.exists()}")

except Exception as e:
    print(f"Error: {e}")
