import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarBooking, Car

bookings = CarBooking.objects.filter(companyid__isnull=True)
count = 0
for booking in bookings:
    if booking.car and booking.car.companyid:
        booking.companyid = booking.car.companyid
        booking.save()
        count += 1
print(f"Backfilled {count} bookings.")

# Check if there are any remaining null companyids where car is null (edge case)
remaining = CarBooking.objects.filter(companyid__isnull=True).count()
print(f"Remaining null companyids: {remaining}")

