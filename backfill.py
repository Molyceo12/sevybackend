import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarBooking

bookings = CarBooking.objects.all().order_by('created_at')
current_id = 1
for b in bookings:
    b.id = current_id
    b.booking_number = f"BKNG-{current_id:03d}-A-0"
    b.save(update_fields=['id', 'booking_number'])
    current_id += 1

print(f"Successfully backfilled {bookings.count()} bookings.")
