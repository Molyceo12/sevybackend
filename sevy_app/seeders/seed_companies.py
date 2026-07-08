import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.serializers.user import CompanyRegistrationSerializer

companies_data = [
    {
        "email": "prestige_rentals@example.com",
        "password": "SecurePassword123!",
        "fullname": "David Kim",
        "company_name": "Prestige Rentals",
        "phone_number": "+250788000001",
        "location": "Kigali Downtown",
        "profile_image": "https://images.unsplash.com/photo-1560179707-f14e90ef3623?w=500&q=80"
    },
    {
        "email": "eco_rides@example.com",
        "password": "SecurePassword123!",
        "fullname": "Sarah Connor",
        "company_name": "Eco Rides Rwanda",
        "phone_number": "+250788000002",
        "location": "Kimironko, Kigali",
        "profile_image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=500&q=80"
    },
    {
        "email": "luxury_fleet_rw@example.com",
        "password": "SecurePassword123!",
        "fullname": "Michael Chang",
        "company_name": "Luxury Fleet RW",
        "phone_number": "+250788000003",
        "location": "Nyarutarama",
        "profile_image": "https://images.unsplash.com/photo-1554469384-e58fac16e23a?w=500&q=80"
    },
    {
        "email": "quick_wheels@example.com",
        "password": "SecurePassword123!",
        "fullname": "Elena Rodriguez",
        "company_name": "Quick Wheels Ltd",
        "phone_number": "+250788000004",
        "location": "Kicukiro",
        "profile_image": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=500&q=80"
    },
    {
        "email": "safari_cruisers@example.com",
        "password": "SecurePassword123!",
        "fullname": "John Mukasa",
        "company_name": "Safari Cruisers",
        "phone_number": "+250788000005",
        "location": "Remera, Kigali",
        "profile_image": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=500&q=80"
    }
]

def seed_companies():
    print("Starting Company Seeding Process...")
    count = 0
    for data in companies_data:
        serializer = CompanyRegistrationSerializer(data=data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                print(f"Successfully created company: {data['company_name']} (User ID: {user.custom_id})")
                count += 1
            except Exception as e:
                print(f"Error saving {data['company_name']}: {e}")
        else:
            print(f"Validation failed for {data['company_name']}: {serializer.errors}")
            
    print(f"Seeding Complete! Successfully seeded {count} companies.")

if __name__ == "__main__":
    seed_companies()
