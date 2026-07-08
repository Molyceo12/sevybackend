import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Driver, Company, Transaction
print("Unapproved Drivers:", Driver.objects.filter(is_approved=False).count())
print("Unverified Companies:", Company.objects.filter(is_verified=False, is_deleted=False).count())
print("Waiting Transactions:", Transaction.objects.filter(status='wait_approval').count())
