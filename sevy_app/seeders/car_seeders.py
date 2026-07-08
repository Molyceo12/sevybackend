import os
import django
import sys
import secrets

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Car

def run():
    print("Starting Car seeder...")
    
    # Delete existing cars to start fresh
    Car.objects.all().delete()
    
    cars_data = [
        {
            "companyid": secrets.token_hex(12),
            "name": "Tesla Model S",
            "brand": "Tesla",
            "description": "A car with high specs that are rented at an affordable price.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9441,
            "location_long": 30.0619,
            "price_per_day": 180000.00,
            "rating": 5.0,
            "reviews_count": 125,
            "capacity_seats": 5,
            "engine_power": "670 HP",
            "max_speed": "250km/h",
            "fuel_range": "405 Miles",
            "advanced_features": ["Autopilot", "Auto Parking"],
            "images": ["assets/images/tesla.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "Toyota Camry",
            "brand": "Toyota",
            "description": "Comfortable and reliable daily driver.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9536,
            "location_long": 30.0605,
            "price_per_day": 150000.00,
            "rating": 4.8,
            "reviews_count": 89,
            "capacity_seats": 5,
            "engine_power": "203 HP",
            "max_speed": "210km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Cruise Control", "Lane Assist"],
            "images": ["assets/images/toyota.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "BMW M4",
            "brand": "BMW",
            "description": "Sporty and luxurious.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9398,
            "location_long": 30.0441,
            "price_per_day": 180000.00,
            "rating": 4.9,
            "reviews_count": 45,
            "capacity_seats": 4,
            "engine_power": "503 HP",
            "max_speed": "290km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Sport Mode", "HUD"],
            "images": ["assets/images/tesla.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "Mercedes Benz C",
            "brand": "Mercedes",
            "description": "Premium comfort and elegance.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9400,
            "location_long": 30.0500,
            "price_per_day": 160000.00,
            "rating": 4.7,
            "reviews_count": 60,
            "capacity_seats": 5,
            "engine_power": "255 HP",
            "max_speed": "240km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Leather Seats", "Sunroof"],
            "images": ["assets/images/toyota.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "Mitsubishi Lancer",
            "brand": "Mitsubishi",
            "description": "Affordable and practical.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9500,
            "location_long": 30.0700,
            "price_per_day": 90000.00,
            "rating": 4.5,
            "reviews_count": 32,
            "capacity_seats": 5,
            "engine_power": "148 HP",
            "max_speed": "200km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Bluetooth", "Backup Camera"],
            "images": ["assets/images/tesla.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "Toyota Corolla",
            "brand": "Toyota",
            "description": "The world's most trusted compact car.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9600,
            "location_long": 30.0800,
            "price_per_day": 120000.00,
            "rating": 4.6,
            "reviews_count": 110,
            "capacity_seats": 5,
            "engine_power": "169 HP",
            "max_speed": "190km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Apple CarPlay", "Safety Sense"],
            "images": ["assets/images/toyota.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "BMW X5",
            "brand": "BMW",
            "description": "Spacious luxury SUV.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9700,
            "location_long": 30.0900,
            "price_per_day": 200000.00,
            "rating": 4.8,
            "reviews_count": 75,
            "capacity_seats": 5,
            "engine_power": "335 HP",
            "max_speed": "243km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Panoramic Roof", "AWD"],
            "images": ["assets/images/tesla.png"]
        },
        {
            "companyid": secrets.token_hex(12),
            "name": "Mercedes Benz E",
            "brand": "Mercedes",
            "description": "Ultimate executive class.",
            "location_name": "Kigali, RW",
            "location_lat": -1.9800,
            "location_long": 30.1000,
            "price_per_day": 250000.00,
            "rating": 5.0,
            "reviews_count": 92,
            "capacity_seats": 5,
            "engine_power": "362 HP",
            "max_speed": "250km/h",
            "fuel_range": "Petrol",
            "advanced_features": ["Massage Seats", "Premium Audio"],
            "images": ["assets/images/toyota.png"]
        }
    ]

    for data in cars_data:
        Car.objects.create(**data)
        
    print(f"Successfully seeded {len(cars_data)} cars!")

if __name__ == "__main__":
    run()
