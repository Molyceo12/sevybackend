import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import ExploreCategory

def seed_categories():
    categories = [
        "nature",
        "cities",
        "mountains",
        "animals",
        "forests",
        "lakes"
    ]

    print("Seeding Explore Categories...")
    count = 0
    for cat in categories:
        # get_or_create to avoid duplicates if run multiple times
        obj, created = ExploreCategory.objects.get_or_create(categoryname=cat)
        if created:
            print(f"  + Created category: {cat} (ID: {obj.id})")
            count += 1
        else:
            print(f"  - Category already exists: {cat} (ID: {obj.id})")

    print(f"Finished! Added {count} new categories.")

if __name__ == '__main__':
    seed_categories()
