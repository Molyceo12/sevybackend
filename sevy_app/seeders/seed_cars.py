import os
import django
import sys
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Car, Company

car_data_templates = [
    {
        "name": "Camry",
        "brand": "Toyota",
        "description": "A highly reliable and comfortable sedan, perfect for navigating Kigali.",
        "price_per_day": 150000.00,
        "capacity_seats": 5,
        "engine_power": "203 HP",
        "max_speed": "210 km/h",
        "fuel_range": "Petrol",
        "advanced_features": ["Bluetooth", "Backup Camera", "Cruise Control"],
        "images": ["assets/images/toyota.png"],
        "location_name": "Kigali, RW",
        "rating": 4.8,
    },
    {
        "name": "M4",
        "brand": "BMW",
        "description": "High-performance sports coupe combining luxury and intense speed.",
        "price_per_day": 180000.00,
        "capacity_seats": 4,
        "engine_power": "473 HP",
        "max_speed": "290 km/h",
        "fuel_range": "Petrol",
        "advanced_features": ["Sport Seats", "Navigation", "Premium Audio"],
        "images": ["assets/images/tesla.png"],
        "location_name": "Kigali, RW",
        "rating": 4.9,
    },
    {
        "name": "C-Class",
        "brand": "Mercedes Benz",
        "description": "Elegant luxury sedan with a premium interior and smooth ride.",
        "price_per_day": 160000.00,
        "capacity_seats": 5,
        "engine_power": "255 HP",
        "max_speed": "240 km/h",
        "fuel_range": "Petrol",
        "advanced_features": ["Leather Seats", "Ambient Lighting", "Sunroof"],
        "images": ["assets/images/toyota.png"],
        "location_name": "Kigali, RW",
        "rating": 4.7,
    },
    {
        "name": "Lancer",
        "brand": "Mitsubishi",
        "description": "Sporty and affordable, a great choice for quick city commutes.",
        "price_per_day": 90000.00,
        "capacity_seats": 5,
        "engine_power": "148 HP",
        "max_speed": "200 km/h",
        "fuel_range": "Petrol",
        "advanced_features": ["Keyless Entry", "Alloy Wheels"],
        "images": ["assets/images/tesla.png"],
        "location_name": "Kigali, RW",
        "rating": 4.5,
    },
    {
        "name": "Corolla",
        "brand": "Toyota",
        "description": "The world's most trusted compact car. Outstanding fuel economy.",
        "price_per_day": 120000.00,
        "capacity_seats": 5,
        "engine_power": "139 HP",
        "max_speed": "180 km/h",
        "fuel_range": "Hybrid",
        "advanced_features": ["Apple CarPlay", "Lane Assist"],
        "images": ["assets/images/toyota.png"],
        "location_name": "Kigali, RW",
        "rating": 4.6,
    },
    {
        "name": "X5",
        "brand": "BMW",
        "description": "A powerful luxury SUV with a commanding presence and spacious interior.",
        "price_per_day": 200000.00,
        "capacity_seats": 5,
        "engine_power": "335 HP",
        "max_speed": "243 km/h",
        "fuel_range": "Diesel",
        "advanced_features": ["AWD", "Panoramic Roof", "Third Row Seating"],
        "images": ["assets/images/tesla.png"],
        "location_name": "Kigali, RW",
        "rating": 4.8,
    },
    {
        "name": "E-Class",
        "brand": "Mercedes Benz",
        "description": "The ultimate executive sedan. Top-tier luxury and cutting-edge technology.",
        "price_per_day": 250000.00,
        "capacity_seats": 5,
        "engine_power": "362 HP",
        "max_speed": "250 km/h",
        "fuel_range": "Hybrid",
        "advanced_features": ["Massage Seats", "Burmester Audio", "Air Suspension"],
        "images": ["assets/images/toyota.png"],
        "location_name": "Kigali, RW",
        "rating": 5.0,
    }
]

def seed_cars():
    companies = list(Company.objects.all())
    
    if not companies:
        print("Error: No companies found! Run seed_companies.py first.")
        return

    print("Deleting old cars...")
    Car.objects.all().delete()

    print("Starting Car Seeding Process...")
    count = 0
    
    for template in car_data_templates:
        # Assign a random company to each car
        company = random.choice(companies)
        
        car = Car.objects.create(
            companyid=company,
            name=template["name"],
            brand=template["brand"],
            description=template["description"], # Guaranteed not null
            price_per_day=template["price_per_day"],
            capacity_seats=template["capacity_seats"],
            engine_power=template["engine_power"], # Guaranteed not null
            max_speed=template["max_speed"], # Guaranteed not null
            fuel_range=template["fuel_range"], # Guaranteed not null
            advanced_features=template["advanced_features"],
            images=template["images"],
            location_name=template["location_name"], # Guaranteed not null
            location_lat=-1.9441, # Hardcoded Kigali latitude (not null)
            location_long=30.0619, # Hardcoded Kigali longitude (not null)
            status='available',
            rating=template["rating"],
            reviews_count=random.randint(50, 150)
        )
        print(f"Created {car.brand} {car.name} for company: {company.company_name or company.host_name}")
        count += 1
        
    print(f"\nSeeding Complete! Successfully seeded {count} cars with EXACT frontend values and ZERO null fields.")

if __name__ == "__main__":
    seed_cars()
