from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from sevy_app.models.user_info import UserInfo

User = get_user_model()

class CustomerRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        error_messages={'required': 'Email is required', 'blank': 'Email cannot be empty'}
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        error_messages={'required': 'Password is required', 'blank': 'Password cannot be empty'}
    )
    fullname = serializers.CharField(
        required=True,
        error_messages={'required': 'Fullname is required', 'blank': 'Fullname cannot be empty'}
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        with transaction.atomic():
            # Create the CustomUser
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                user_type='customer'
            )
            # Create the associated UserInfo
            UserInfo.objects.create(
                user=user,
                full_names=validated_data['fullname']
            )
            return user

class DriverRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        error_messages={'required': 'Email is required', 'blank': 'Email cannot be empty'}
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        error_messages={'required': 'Password is required', 'blank': 'Password cannot be empty'}
    )
    fullname = serializers.CharField(
        required=True,
        error_messages={'required': 'Fullname is required', 'blank': 'Fullname cannot be empty'}
    )
    vehicle_make_color = serializers.CharField(
        required=True,
        error_messages={'required': 'Vehicle make and color is required', 'blank': 'Vehicle make and color cannot be empty'}
    )
    plate_number = serializers.CharField(
        required=True,
        error_messages={'required': 'Plate number is required', 'blank': 'Plate number cannot be empty'}
    )
    phone_number = serializers.CharField(
        required=True,
        error_messages={'required': 'Phone number is required', 'blank': 'Phone number cannot be empty'}
    )
    driving_license = serializers.URLField(
        required=True,
        error_messages={'required': 'Driving license URL is required', 'blank': 'Driving license URL cannot be empty'}
    )
    government_id = serializers.URLField(
        required=True,
        error_messages={'required': 'Government ID URL is required', 'blank': 'Government ID URL cannot be empty'}
    )
    experience_years = serializers.IntegerField(
        required=True,
        error_messages={'required': 'Experience years is required', 'invalid': 'Experience must be a valid number'}
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        from sevy_app.models import Driver
        with transaction.atomic():
            # Create the CustomUser
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                user_type='driver'
            )
            # Create the associated UserInfo
            UserInfo.objects.create(
                user=user,
                full_names=validated_data['fullname']
            )
            # Create the Driver Profile
            Driver.objects.create(
                userid=user,
                full_name=validated_data['fullname'],
                vehicle_make_color=validated_data['vehicle_make_color'],
                plate_number=validated_data['plate_number'],
                phone_number=validated_data['phone_number'],
                driving_license=validated_data.get('driving_license'),
                government_id=validated_data.get('government_id'),
                experience_years=validated_data['experience_years']
            )
            return user

class CompanyRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        error_messages={'required': 'Email is required', 'blank': 'Email cannot be empty'}
    )
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        error_messages={'required': 'Password is required', 'blank': 'Password cannot be empty'}
    )
    fullname = serializers.CharField(
        required=True,
        error_messages={'required': 'Fullname is required', 'blank': 'Fullname cannot be empty'}
    )
    company_name = serializers.CharField(
        required=False,
        allow_blank=True
    )
    company_type = serializers.ChoiceField(
        choices=['carrental', 'tourism'],
        required=True,
        error_messages={'required': 'Company type is required', 'invalid_choice': 'Invalid company type'}
    )
    phone_number = serializers.CharField(
        required=True,
        error_messages={'required': 'Phone number is required', 'blank': 'Phone number cannot be empty'}
    )
    location = serializers.CharField(
        required=False,
        allow_blank=True
    )
    profile_image = serializers.CharField(
        required=False,
        allow_blank=True
    )
    rdb_certificate_url = serializers.CharField(
        required=False,
        allow_blank=True
    )
    owner_id_url = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        from sevy_app.models import Company
        with transaction.atomic():
            # Create the CustomUser
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                user_type='company'
            )
            # Create the associated UserInfo
            UserInfo.objects.create(
                user=user,
                full_names=validated_data['fullname']
            )
            # Create the Company Profile
            Company.objects.create(
                company_id=user,
                host_name=validated_data['fullname'],
                company_name=validated_data.get('company_name', ''),
                contact_email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                location=validated_data.get('location', ''),
                profile_image=validated_data.get('profile_image', ''),
                company_type=validated_data['company_type'],
                rdb_certificate_url=validated_data.get('rdb_certificate_url', ''),
                owner_id_url=validated_data.get('owner_id_url', '')
            )
            return user
