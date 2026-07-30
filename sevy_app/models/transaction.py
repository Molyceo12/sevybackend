import secrets
from django.db import models
from django.conf import settings

def generate_transaction_id():
    return secrets.token_hex(12)

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=50, primary_key=True, default=generate_transaction_id)
    TRANSACTION_TYPE_CHOICES = (
        ('trip', 'Trip'),
        ('withdrawal', 'Withdrawal'),
        ('carbooking', 'Car Booking'),
        ('cartripbooking', 'Car Trip Booking'),
        ('platform_commission', 'Platform Commission'),
    )

    STATUS_CHOICES = (
        ('waitingapproval', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='transactions', null=True, blank=True)
    reference_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES, default='trip')
    related_id = models.CharField(max_length=100, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='RWF')
    
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waitingapproval')
    customer_approved = models.BooleanField(default=False, help_text="Set to True when customer approves the booking is completed")
    description = models.TextField(null=True, blank=True)
    
    tracking_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            last_tx = Transaction.objects.filter(tracking_number__startswith='TRX-').order_by('-created_at').first()
            if last_tx and last_tx.tracking_number:
                parts = last_tx.tracking_number.split('-')
                if len(parts) >= 2:
                    try:
                        seq = int(parts[1])
                        new_seq = seq + 1
                    except ValueError:
                        new_seq = 0
                else:
                    new_seq = 0
            else:
                new_seq = 0
            while True:
                candidate = f"TRX-{new_seq:03d}-A-1"
                if not Transaction.objects.filter(tracking_number=candidate).exists():
                    self.tracking_number = candidate
                    break
                new_seq += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.tracking_number or self.transaction_id} - {self.amount} {self.currency} ({self.status})"
