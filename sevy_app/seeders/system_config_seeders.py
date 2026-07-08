import os
import sys
import django

# Setup Django environment so we can use models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import SystemConfig

def seed_system_config():
    print("Starting system configuration seeder...")

    # We always use id=1 to ensure it's a singleton configuration row
    config, created = SystemConfig.objects.get_or_create(
        id=1,
        defaults={
            'cost_per_km': 350.00,
            'driver_only_cost_per_km': 150.00,
            'choose_driver_fee_percentage': 20.00
        }
    )
    
    if not created:
        config.cost_per_km = 350.00
        config.driver_only_cost_per_km = 150.00
        config.choose_driver_fee_percentage = 20.00
        config.save()
        print("Updated existing configuration.")
    else:
        print("Created new system configuration.")

    print("\nSuccessfully seeded system configuration!")

if __name__ == '__main__':
    seed_system_config()
