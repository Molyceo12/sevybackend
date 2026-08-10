import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy_backend.settings')
django.setup()

from sevy_app.models import Transaction
transactions = Transaction.objects.filter(user__user_type='driver').order_by('-created_at')

withdrawals = [t for t in transactions if t.transaction_type == 'withdrawal']
print(f"Total withdrawals: {len(withdrawals)}")
for w in withdrawals:
    print(f"ID: {w.transaction_id}, Status: {w.status}, Amount: {w.amount}, User: {w.user.email}, Type: {w.transaction_type}")
