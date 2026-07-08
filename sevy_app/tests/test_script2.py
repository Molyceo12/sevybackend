import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarBooking

booking = CarBooking.objects.filter(booking_id="09dc475b37e402a865078778").first()
if booking:
    print(f"Booking companyid: {booking.companyid}")
    if booking.companyid:
        print(f"Booking company user: {booking.companyid.user}")
