import os
import sys
import django

# Setup Django environment so we can use models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Location, CustomUser

def seed_locations():
    print("Starting location seeder...")
    
    # Ensure we have at least one user to assign locations to
    user = CustomUser.objects.first()
    if not user:
        user = CustomUser.objects.create_user(
            email="seed_user@example.com",
            password="password123",
            user_type="admin"
        )
        print('Created default seed user.')

    rwanda_locations = [
        {"name": "Nyamirambo, Kigali", "lat": -1.9840, "lng": 30.0440},
        {"name": "Remera, Kigali", "lat": -1.9560, "lng": 30.1110},
        {"name": "Kimironko, Kigali", "lat": -1.9540, "lng": 30.1340},
        {"name": "Nyarutarama, Kigali", "lat": -1.9360, "lng": 30.0930},
        {"name": "Gisozi, Kigali", "lat": -1.9280, "lng": 30.0630},
        {"name": "Kicukiro, Kigali", "lat": -1.9960, "lng": 30.0980},
        {"name": "Kiyovu, Kigali", "lat": -1.9480, "lng": 30.0640},
        {"name": "Gikondo, Kigali", "lat": -1.9820, "lng": 30.0760},
        {"name": "Kacyiru, Kigali", "lat": -1.9420, "lng": 30.0820},
        {"name": "Gacuriro, Kigali", "lat": -1.9250, "lng": 30.0950},
        {"name": "Bumbogo, Kigali", "lat": -1.8950, "lng": 30.1450},
        {"name": "Kanombe, Kigali", "lat": -1.9680, "lng": 30.1350},
        {"name": "Masaka, Kigali", "lat": -1.9950, "lng": 30.1800},
        {"name": "Ndera, Kigali", "lat": -1.9460, "lng": 30.1550},
        {"name": "Rusororo, Kigali", "lat": -1.9850, "lng": 30.2050},
        {"name": "Kinyinya, Kigali", "lat": -1.9160, "lng": 30.0960},
        {"name": "Gitega, Kigali", "lat": -1.9540, "lng": 30.0520},
        {"name": "Muhima, Kigali", "lat": -1.9420, "lng": 30.0580},
        {"name": "Niboye, Kigali", "lat": -1.9820, "lng": 30.1020},
        {"name": "Gatenga, Kigali", "lat": -1.9950, "lng": 30.0850},
    ]

    count = 0
    for loc in rwanda_locations:
        obj, created = Location.objects.get_or_create(
            user=user,
            locationname=loc["name"],
            defaults={
                "latitude": loc["lat"],
                "longitude": loc["lng"]
            }
        )
        if created:
            count += 1
    
    print(f'Successfully seeded {count} new Rwandan locations to the database!')

if __name__ == '__main__':
    seed_locations()
