import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarBooking

booking = CarBooking.objects.filter(booking_id="4af0ffa589cc5531af180de9").first()
if booking:
    print(f"Booking found: {booking}")
    company_user = None
    if booking.companyid and booking.companyid.user:
        company_user = booking.companyid.user
    elif booking.car and booking.car.companyid and booking.car.companyid.user:
        company_user = booking.car.companyid.user
    print(f"Company User to receive payout: {company_user}")
else:
    print("Booking not found")
