import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sevy.settings")
django.setup()

from sevy_app.models import Trip

print("Starting test...")
userid = "2309b77cc2d1fb2cc9a46783"

print("Running query...")
# Try the exact query that is in get_user_trips.py
trips = Trip.objects.filter(userid_id=userid).order_by('-created_at')
print(f"Query returned {trips.count()} trips.")

print("Iterating over trips...")
for trip in trips:
    print(f"Trip: {trip.trip_id}")
    if trip.driverid:
        print(f"Driver ID: {trip.driverid}")
        try:
            print(f"Driver User ID: {trip.driverid.userid.custom_id}")
        except Exception as e:
            print(f"Error accessing driver userid: {e}")

print("Done.")
