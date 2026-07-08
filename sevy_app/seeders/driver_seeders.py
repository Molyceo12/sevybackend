import os
import sys
import django
import random

# Setup Django environment so we can use models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from django.contrib.auth import get_user_model
from sevy_app.models import Driver, DriverLocation

User = get_user_model()

def seed_driver_data():
    print("Starting driver and driver_location data seeder...")

    drivers_data = [
        {"name": "Kagabo Eric", "email": "kagabo@sevy.com", "car": "Toyota Corolla · White", "plate": "RAB 123 A", "place": "Kigali, Nyamirambo", "lat": -1.9680, "long": 30.0470},
        {"name": "Mugisha Jean", "email": "mugisha@sevy.com", "car": "Hyundai Elantra · Silver", "plate": "RCA 456 B", "place": "Kigali, Kimironko", "lat": -1.9441, "long": 30.1264},
        {"name": "Uwase Marie", "email": "uwase@sevy.com", "car": "Kia Rio · Red", "plate": "RAB 789 C", "place": "Kigali, Kicukiro", "lat": -1.9904, "long": 30.1082},
        {"name": "Mutesi Alice", "email": "mutesi@sevy.com", "car": "Toyota Yaris · Blue", "plate": "RCA 321 D", "place": "Kigali, Nyarutarama", "lat": -1.9366, "long": 30.0984},
        {"name": "Niyomugabo Patrick", "email": "niyomugabo@sevy.com", "car": "Nissan Sentra · Black", "plate": "RAB 654 E", "place": "Kigali, Remera", "lat": -1.9587, "long": 30.1130},
        {"name": "Kalisa Claude", "email": "kalisa@sevy.com", "car": "Toyota RAV4 · Grey", "plate": "RCA 987 F", "place": "Kigali, Gisozi", "lat": -1.9255, "long": 30.0617},
        {"name": "Mukandoli Chantal", "email": "mukandoli@sevy.com", "car": "Honda Civic · White", "plate": "RAB 111 G", "place": "Kigali, Kiyovu", "lat": -1.9547, "long": 30.0653},
        {"name": "Mutoni Grace", "email": "mutoni@sevy.com", "car": "Suzuki Swift · Yellow", "plate": "RCA 222 H", "place": "Kigali, Gikondo", "lat": -1.9790, "long": 30.0760},
        {"name": "Habimana Emmanuel", "email": "habimana@sevy.com", "car": "Toyota Prius · Silver", "plate": "RAB 333 I", "place": "Kigali, Kacyiru", "lat": -1.9355, "long": 30.0734},
        {"name": "Iradukunda Kevin", "email": "iradukunda@sevy.com", "car": "Hyundai Accent · Blue", "plate": "RCA 444 J", "place": "Kigali, Nyamata", "lat": -2.1581, "long": 30.0901},
    ]

    count = 0
    for item in drivers_data:
        # Create User
        user, user_created = User.objects.get_or_create(
            email=item["email"],
            defaults={
                "user_type": "driver",
            }
        )
        if user_created:
            user.set_password("password123")
            user.save()

        # Create Driver Profile
        driver_obj, driver_created = Driver.objects.get_or_create(
            userid=user,
            defaults={
                "full_name": item["name"],
                "vehicle_make_color": item["car"],
                "plate_number": item["plate"],
                "is_approved": True,
            }
        )

        if not driver_created:
            driver_obj.full_name = item["name"]
            driver_obj.vehicle_make_color = item["car"]
            driver_obj.plate_number = item["plate"]
            driver_obj.is_approved = True
            driver_obj.save()

        # Create Driver Location
        loc_obj, loc_created = DriverLocation.objects.get_or_create(
            userid=user,
            defaults={
                "lat": item["lat"],
                "long": item["long"],
                "place": item["place"],
            }
        )

        if not loc_created:
            loc_obj.lat = item["lat"]
            loc_obj.long = item["long"]
            loc_obj.place = item["place"]
            loc_obj.save()

        count += 1
        print(f"Processed Driver: {item['name']}")

    print(f"\nSuccessfully seeded {count} drivers and their locations!")

if __name__ == '__main__':
    seed_driver_data()
