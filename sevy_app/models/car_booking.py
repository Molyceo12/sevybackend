import secrets
from django.db import models
from django.conf import settings

def generate_booking_id():
    return secrets.token_hex(12)

class CarBooking(models.Model):
    BOOKING_TYPE_CHOICES = (
        ('self_drive', 'Self Drive'),
        ('with_driver', 'With Driver'),
    )
    
    CLIENT_SEX_CHOICES = (
        ('any', 'Any'),
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    RENTAL_PLAN_CHOICES = (
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Currently Rented'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    DRIVER_STATUS_CHOICES = (
        ('waiting', 'Waiting for Driver'),
        ('accepted', 'Driver Accepted'),
        ('rejected', 'Driver Rejected'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )

    ADMIN_APPROVAL_CHOICES = (
        ('none', 'None'),
        ('driver', 'Driver'),
        ('company', 'Company'),
        ('both', 'Both'),
    )

    CUSTOMER_APPROVAL_CHOICES = (
        ('waiting', 'Waiting'),
        ('requestsent', 'Request Sent'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    )

    booking_id = models.CharField(max_length=50, primary_key=True, default=generate_booking_id)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='car_bookings')
    car = models.ForeignKey('sevy_app.Car', on_delete=models.CASCADE, related_name='bookings')
    companyid = models.ForeignKey('sevy_app.Company', on_delete=models.CASCADE, related_name='company_bookings')
    company_user_link = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_company_bookings')
    driver = models.ForeignKey('sevy_app.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='car_bookings')
    
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES)
    client_sex = models.CharField(max_length=10, choices=CLIENT_SEX_CHOICES, default='any')
    rental_plan = models.CharField(max_length=20, choices=RENTAL_PLAN_CHOICES)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    driver_status = models.CharField(max_length=20, choices=DRIVER_STATUS_CHOICES, null=True, blank=True)
    admin_company_approval = models.CharField(max_length=20, choices=CUSTOMER_APPROVAL_CHOICES, default='waiting')
    admin_driver_approval = models.CharField(max_length=20, choices=CUSTOMER_APPROVAL_CHOICES, default='waiting')
    customer_approval_status = models.CharField(max_length=20, choices=CUSTOMER_APPROVAL_CHOICES, default='waiting')
    company_customer_approval = models.CharField(max_length=20, choices=CUSTOMER_APPROVAL_CHOICES, default='waiting')
    driver_customer_approval = models.CharField(max_length=20, choices=CUSTOMER_APPROVAL_CHOICES, null=True, blank=True)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    transaction = models.ForeignKey('sevy_app.Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='car_bookings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    id = models.IntegerField(unique=True, editable=False)
    booking_number = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.id:
            max_id = CarBooking.objects.aggregate(models.Max('id'))['id__max']
            self.id = 1 if max_id is None else max_id + 1
        
        if not self.booking_number:
            self.booking_number = f"BKNG-{self.id:03d}-A-0"
            
        super(CarBooking, self).save(*args, **kwargs)

    class Meta:
        db_table = 'car_bookings'
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.status}"
