import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Trip, CarBooking

trips = Trip.objects.all().values()
bookings = CarBooking.objects.all().values()

print("TRIPS:")
for t in trips:
    print(t['id'], t['status'], t.get('driver_status', 'N/A'))

print("BOOKINGS:")
for b in bookings:
    print(b['id'], b['status'], b.get('driver_status', 'N/A'))
