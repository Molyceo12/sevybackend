import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarBooking

booking = CarBooking.objects.filter(booking_id="09dc475b37e402a865078778").first()
if booking:
    print(f"Car: {booking.car}")
    if booking.car:
        print(f"Company for Car: {booking.car.companyid}")
        if booking.car.companyid:
            print(f"User for Company: {booking.car.companyid.user}")
else:
    print("Booking not found")
