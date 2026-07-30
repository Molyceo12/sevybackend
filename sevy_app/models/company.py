import secrets
from django.db import models

def generate_company_id():
    return secrets.token_hex(12)

class Company(models.Model):
    company_id = models.OneToOneField('sevy_app.CustomUser', on_delete=models.CASCADE, primary_key=True, related_name='company_profile', help_text="Links to auth User for password & login", db_column='company_id')
    host_name = models.CharField(max_length=255, help_text="Name of the individual host/owner e.g. Hela Quintin")
    company_name = models.CharField(max_length=255, null=True, blank=True, help_text="Optional name of the registered company")
    
    COMPANY_TYPE_CHOICES = (
        ('carrental', 'Car Rental'),
        ('tourism', 'Tourism'),
    )
    company_type = models.CharField(
        max_length=20, 
        choices=COMPANY_TYPE_CHOICES, 
        default='carrental',
        help_text="Type of the company"
    )

    profile_image = models.CharField(max_length=500, null=True, blank=True, help_text="URL or path to profile image")
    is_verified = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False, help_text="True if the company registration was denied/cancelled")
    cancellation_reason = models.CharField(max_length=500, null=True, blank=True, help_text="Reason for cancellation/denial")
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    
    rdb_certificate_url = models.CharField(max_length=500, null=True, blank=True, help_text="URL or path to business registration certificate")
    owner_id_url = models.CharField(max_length=500, null=True, blank=True, help_text="URL or path to owner ID or passport")
    
    location = models.CharField(max_length=255, null=True, blank=True, help_text="Registered location/address")
    
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Current wallet balance")
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Accumulated bonuses")
    
    total_bookings = models.IntegerField(default=0, help_text="Cached total number of bookings")
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Cached total income")
    
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag for the company")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name or self.host_name} ({self.company_id})"
