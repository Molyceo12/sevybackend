import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Car, CustomUser

car = Car.objects.first()
user = CustomUser.objects.filter(user_type='customer').first()

print(f"Car ID: {car.car_id if car else 'None'}")
print(f"User ID: {user.custom_id if user else 'None'}")
