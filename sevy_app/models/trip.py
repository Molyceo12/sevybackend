import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone

def generate_trip_id():
    return secrets.token_hex(12)

class Trip(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    SERVICE_TYPE_CHOICES = (
        ('driver_and_car', 'Driver & Car'),
        ('driver_only', 'Driver Only'),
    )

    TRIP_TYPE_CHOICES = (
        ('instanttrip', 'Instant Trip'),
        ('scheduledtrip', 'Scheduled Trip'),
    )

    DRIVER_STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('coming', 'Coming'),
        ('rejected', 'Rejected'),
    )

    APPROVAL_STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('requestsent', 'Request Sent'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('momo', 'Mobile Money'),
    )

    trip_id = models.CharField(max_length=50, primary_key=True, default=generate_trip_id)
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_trips')
    driverid = models.ForeignKey('sevy_app.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_trips')
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='driver_and_car')
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='instanttrip')
    driver_status = models.CharField(max_length=20, choices=DRIVER_STATUS_CHOICES, default='waiting')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='waiting')
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estimated_time = models.CharField(max_length=50, help_text="e.g., '15 mins'")
    trip_distance_km = models.FloatField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    transaction = models.ForeignKey('sevy_app.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    
    start_lat = models.FloatField(null=True, blank=True)
    start_long = models.FloatField(null=True, blank=True)
    start_place_name = models.CharField(max_length=255, null=True, blank=True)
    
    destination_lat = models.FloatField(null=True, blank=True)
    destination_long = models.FloatField(null=True, blank=True)
    destination_name = models.CharField(max_length=255, null=True, blank=True)
    
    tracking_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'trips'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            last_trip = Trip.objects.filter(tracking_number__startswith='TRP-').order_by('-tracking_number').first()
            if last_trip and last_trip.tracking_number:
                parts = last_trip.tracking_number.split('-')
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
            self.tracking_number = f"TRP-{new_seq:03d}-A-1"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trip {self.tracking_number or self.trip_id} ({self.status})"
