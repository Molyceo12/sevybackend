import secrets
from django.db import models
from django.conf import settings

def generate_commission_id():
    return secrets.token_hex(12)

class PlatformCommission(models.Model):
    commission_id = models.CharField(max_length=50, primary_key=True, default=generate_commission_id)
    source_type = models.CharField(max_length=50, help_text="e.g., 'carbooking', 'trip'")
    related_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='platform_commissions', null=True, blank=True)
    transaction = models.ForeignKey('sevy_app.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='commissions')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    commission_earned = models.DecimalField(max_digits=12, decimal_places=2)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_commissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Commission {self.commission_id} - {self.commission_earned} RWF"
