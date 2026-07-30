from django.core.management.base import BaseCommand
from sevy_app.models import Trip, CarBooking, Transaction, Notification, Driver, Company

class Command(BaseCommand):
    help = 'Clears test data from transactional tables (Trips, Bookings, Transactions, Notifications) to improve performance'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting test data deletion using RAW SQL..."))

        from django.db import connection
        with connection.cursor() as cursor:
            # Delete in order to avoid foreign key constraints
            cursor.execute("DELETE FROM platform_commissions;")
            self.stdout.write(self.style.SUCCESS("Emptied platform_commissions table."))
            
            cursor.execute("DELETE FROM trips;")
            self.stdout.write(self.style.SUCCESS("Emptied trips table."))
            
            cursor.execute("DELETE FROM car_bookings;")
            self.stdout.write(self.style.SUCCESS("Emptied car_bookings table."))
            
            cursor.execute("DELETE FROM transactions;")
            self.stdout.write(self.style.SUCCESS("Emptied transactions table."))
            
            # For notifications, the table name is typically appname_notification unless overridden
            # We'll use the ORM for notifications just in case the table name is different
            notif_count, _ = Notification.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {notif_count} Notifications."))

        # 5. Reset Balances & Bonuses to 0.00 for Drivers
        Driver.objects.update(balance=0.00, bonus=0.00)
        self.stdout.write(self.style.SUCCESS("Reset all Driver balances and bonuses to 0.00."))

        # 6. Reset Balances & Bonuses to 0.00 for Companies
        Company.objects.update(balance=0.00, bonuses=0.00)
        self.stdout.write(self.style.SUCCESS("Reset all Company balances and bonuses to 0.00."))

        self.stdout.write(self.style.SUCCESS("Successfully cleared test data!"))
