import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarBooking, Transaction, Notification, Trip
try:
    from sevy_app.models import PlatformCommission
except ImportError:
    PlatformCommission = None

print("Deleting records...")

bookings_count, _ = CarBooking.objects.all().delete()
print(f"Deleted {bookings_count} CarBooking records.")

trx_count, _ = Transaction.objects.all().delete()
print(f"Deleted {trx_count} Transaction records.")

if PlatformCommission:
    comm_count, _ = PlatformCommission.objects.all().delete()
    print(f"Deleted {comm_count} PlatformCommission records.")
else:
    print("PlatformCommission model not found.")

notif_count, _ = Notification.objects.all().delete()
print(f"Deleted {notif_count} Notification records.")

trip_count, _ = Trip.objects.all().delete()
print(f"Deleted {trip_count} Trip records.")

print("Finished clearing specified tables.")
