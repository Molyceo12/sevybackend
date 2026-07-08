import secrets
from django.db import models
from django.conf import settings

def generate_car_id():
    return secrets.token_hex(12)

from .company import Company

class Car(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
    )

    id = models.IntegerField(unique=True, null=True, blank=True, editable=False)
    car_id = models.CharField(max_length=50, primary_key=True, default=generate_car_id)
    companyid = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='companyid', related_name='cars', help_text="ID of the company or owner")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_deleted = models.BooleanField(default=False)
    
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    location_name = models.CharField(max_length=255)
    location_lat = models.FloatField(null=True, blank=True)
    location_long = models.FloatField(null=True, blank=True)
    
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    reviews_count = models.IntegerField(default=0)
    
    # Specs
    capacity_seats = models.IntegerField(default=4)
    engine_power = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. 670 HP")
    max_speed = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. 250km/h")
    fuel_range = models.CharField(max_length=100, null=True, blank=True, help_text="e.g. 405 Miles or Electric")
    
    advanced_features = models.JSONField(default=list, help_text="Array of feature names e.g. ['Autopilot', 'Auto Parking']")
    images = models.JSONField(default=list, help_text="Array of image paths or URLs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cars'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.id:
            max_id = Car.objects.aggregate(models.Max('id'))['id__max']
            self.id = 1 if max_id is None else max_id + 1
        super(Car, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.car_id})"
