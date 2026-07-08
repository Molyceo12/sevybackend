import os
import sys
import django

# Setup Django environment so we can use models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import Explore, ExploreCategory

def seed_explore_data():
    print("Starting explore data seeder...")

    dummy_company_id = "seed_company_123"

    explore_data = [
        # Nature
        {
            "name": "Akagera",
            "category": "nature",
            "subcategory": "(National Park)",
            "features": ["Savanna", "Wildlife"],
            "images": ["assets/images/akagera.jpeg"],
            "place": "Eastern Province"
        },
        {
            "name": "Nyungwe",
            "category": "nature",
            "subcategory": "(National Park)",
            "features": ["Rainforest", "Primates"],
            "images": ["assets/images/nyungwe.jpeg"],
            "place": "Southern Province"
        },
        {
            "name": "Bigogwe",
            "category": "nature",
            "subcategory": "(Green Hills)",
            "features": ["Cowboys", "Nature"],
            "images": ["assets/images/bigogwe.jpeg"],
            "place": "Western Province"
        },
        {
            "name": "Gishwati",
            "category": "nature",
            "subcategory": "(Mukura National Park)",
            "features": ["Forest", "Chimps"],
            "images": ["assets/images/gishwati.jpeg"],
            "place": "North-Western Province"
        },
        # Cities
        {
            "name": "Rubavu",
            "category": "cities",
            "subcategory": "(Lake Kivu)",
            "features": ["Beaches", "Relaxation"],
            "images": ["assets/images/rubavu.jpeg"],
            "place": "Western Province"
        },
        {
            "name": "Musanze",
            "category": "cities",
            "subcategory": "(Volcanoes)",
            "features": ["Gorillas", "Hiking"],
            "images": ["assets/images/musanze.jpeg"],
            "place": "Northern Province"
        },
        {
            "name": "Muhanga",
            "category": "cities",
            "subcategory": "(Central)",
            "features": ["Culture", "Hills"],
            "images": ["assets/images/muhanga.jpg"],
            "place": "Southern Province"
        },
        {
            "name": "Huye",
            "category": "cities",
            "subcategory": "(Butare)",
            "features": ["Museum", "Heritage"],
            "images": ["assets/images/huye.jpeg"],
            "place": "Southern Province"
        },
    ]

    count = 0
    for item in explore_data:
        # Fetch the category object
        try:
            category_obj = ExploreCategory.objects.get(categoryname=item["category"])
        except ExploreCategory.DoesNotExist:
            print(f"Error: Category '{item['category']}' does not exist. Run explore_categories.py seeder first!")
            continue

        obj, created = Explore.objects.get_or_create(
            name=item["name"],
            defaults={
                "companyid": dummy_company_id,
                "category": category_obj,
                "subcategory": item["subcategory"],
                "features": item["features"],
                "images": item["images"],
                "place": item["place"],
            }
        )
        if created:
            count += 1
            print(f"Added {item['name']} to Explore table.")
        else:
            # Update existing records with new structure (like images)
            obj.features = item["features"]
            obj.images = item["images"]
            obj.category = category_obj
            obj.save()
            print(f"Updated {item['name']} in Explore table.")

    print(f"\nSuccessfully seeded {count} new explore locations!")

if __name__ == '__main__':
    seed_explore_data()
