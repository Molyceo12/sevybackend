from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('trip', 'Trip Alert'),
        ('rental', 'Rental Booking'),
        ('transaction', 'Payment Transaction'),
        ('system', 'System Broadcast'),
        ('promotional', 'Promotional'),
        ('trip_approval', 'Trip Approval'),
        ('booking_cancelled', 'Booking Cancelled'),
    ]

    notification_id = models.CharField(max_length=24, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    
    # Generic linking to Trip, Booking, or Transaction IDs
    related_id = models.CharField(max_length=24, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.notification_id:
            self.notification_id = uuid.uuid4().hex[:24]
        super(Notification, self).save(*args, **kwargs)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"
