from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import string
import random

import secrets

def generate_custom_id():
    # Generates a 24-character hex string (like 6a17f86d0a0fc0364bd9d6d7)
    return secrets.token_hex(12)
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)
        
        # Make sure user_type is admin
        user.user_type = 'admin'
        user.save(using=self._db)
        
        # Create linked profiles for Universal Account access
        try:
            from sevy_app.models.user_info import UserInfo
            from sevy_app.models.company import Company
            from sevy_app.models.driver import Driver
            
            UserInfo.objects.get_or_create(
                user=user,
                defaults={'full_names': 'System Admin'}
            )
            
            Company.objects.get_or_create(
                company_id=user,
                defaults={
                    'host_name': 'Admin Company',
                    'balance': 0.0,
                    'is_verified': True
                }
            )
            
            Driver.objects.get_or_create(
                userid=user,
                defaults={
                    'full_name': 'Admin Driver',
                    'is_approved': True,
                    'balance': 0.0
                }
            )
        except Exception as e:
            print(f"Note: Could not create linked profiles for admin: {e}")
            
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('driver', 'Driver'),
        ('customer', 'Customer'),
        ('company', 'Company'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    custom_id = models.CharField(max_length=50, primary_key=True, default=generate_custom_id)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'sevyuser'

    def __str__(self):
        return self.email
