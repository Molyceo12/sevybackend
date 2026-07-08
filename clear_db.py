import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Company, CarBooking, Transaction, PlatformCommission, Car, Driver

# Delete transactions and commissions first
print(f"Deleting {Transaction.objects.count()} transactions...")
Transaction.objects.all().delete()

print(f"Deleting {PlatformCommission.objects.count()} platform commissions...")
PlatformCommission.objects.all().delete()

print(f"Deleting {CarBooking.objects.count()} bookings...")
CarBooking.objects.all().delete()

print(f"Deleting {Car.objects.count()} cars...")
Car.objects.all().delete()

print(f"Deleting {Company.objects.count()} companies...")
Company.objects.all().delete()

print("Database cleared and ready for new transactions.")
