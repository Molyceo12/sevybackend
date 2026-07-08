from django.db import models
from django.conf import settings

class Driver(models.Model):
    userid = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='driver_profile')
    companyid = models.ForeignKey('sevy_app.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers')
    company_user_link = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    vehicle_make_color = models.CharField(max_length=255)
    plate_number = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    driving_license = models.FileField(upload_to='driver_documents/licenses/', null=True, blank=True)
    government_id = models.FileField(upload_to='driver_documents/ids/', null=True, blank=True)
    home_location_name = models.CharField(max_length=255, null=True, blank=True)
    home_latitude = models.FloatField(null=True, blank=True)
    home_longitude = models.FloatField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(null=True, blank=True)
    
    # Demographics & Experience
    sex = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female')), default='Male')
    experience_years = models.IntegerField(default=0)
    
    # Financials
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'drivers'

    def __str__(self):
        return f"{self.full_name} ({self.userid.email})"
