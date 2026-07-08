import os
import sys
import django
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Company

def run():
    print("Starting Company seeder...")
    
    companies = Company.objects.all()
    if not companies.exists():
        print("No companies found! Make sure cars are seeded first so companies are generated.")
        return

    # Realistic mock data
    host_names = ["Hela Quintin", "Maurice Kigali", "John Doe", "Jane Smith", "Aubin Ishimwe", "Alice Uwase"]
    company_names = ["Hela Rentals Ltd", "Kigali Drives", "Premium Autos", "Sevy Fleet", "Reliable Rides", "Elite Motors"]
    profile_images = [
        "https://randomuser.me/api/portraits/men/32.jpg",
        "https://randomuser.me/api/portraits/women/44.jpg",
        "https://randomuser.me/api/portraits/men/85.jpg",
        "https://randomuser.me/api/portraits/women/12.jpg"
    ]
    
    updated_count = 0
    for company in companies:
        # Generate some realistic data
        is_verified = random.choice([True, True, False]) # 66% chance to be verified
        host_name = random.choice(host_names)
        company_name = random.choice(company_names) if random.choice([True, False]) else None
        
        # Phone generation (Rwandan format for realism)
        phone = f"+25078{random.randint(1000000, 9999999)}"
        
        # Email generation
        email_prefix = host_name.lower().replace(" ", ".")
        email = f"{email_prefix}@example.com"
        
        company.host_name = host_name
        company.company_name = company_name
        company.profile_image = random.choice(profile_images)
        company.is_verified = is_verified
        company.phone_number = phone
        company.contact_email = email
        
        company.save()
        updated_count += 1

    print(f"Successfully updated and seeded {updated_count} companies with realistic data!")

if __name__ == "__main__":
    run()
