import os
import sys
import django
import random
from django.db.models import Avg

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models import CarReview, Car, CustomUser

def seed_reviews():
    # Clear existing reviews
    CarReview.objects.all().delete()
    print("Deleted all existing car reviews.")

    cars = list(Car.objects.all())
    users = list(CustomUser.objects.all())

    if len(users) < 2:
        print("Error: Need at least 2 users in the database to seed reviews properly.")
        return

    print(f"Found {len(cars)} cars and {len(users)} users. Beginning seeding...")

    review_templates = [
        (5.0, "Absolutely amazing car! Smooth ride and perfectly clean."),
        (4.5, "Great experience overall. The car was well-maintained."),
        (4.8, "Loved the features and comfort. Will rent again!"),
        (5.0, "Best rental experience I've had. Highly recommended."),
        (4.0, "Good car, but pickup was slightly delayed. Still highly recommend."),
        (4.7, "Very comfortable and fuel-efficient for my long trip."),
        (5.0, "Flawless! The host was super communicative and the car was pristine."),
        (4.2, "Solid ride. Met all my expectations for a weekend getaway."),
        (4.9, "Incredible performance. Felt very luxurious and safe."),
    ]

    total_created = 0

    for car in cars:
        # Give each car 2 to 4 random reviews (but max out at the number of users)
        num_reviews = min(random.randint(2, 4), len(users))
        
        # Select unique users for this car
        reviewers = random.sample(users, num_reviews)
        
        for user in reviewers:
            rating, text = random.choice(review_templates)
            
            CarReview.objects.create(
                user=user,
                car=car,
                rating=rating,
                review_text=text
            )
            total_created += 1
            
        # Update Car aggregates
        reviews = CarReview.objects.filter(car=car)
        car.reviews_count = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        car.rating = round(avg_rating, 1) if avg_rating else 0.0
        car.save()

    print(f"Successfully seeded {total_created} reviews across {len(cars)} cars.")
    print("Car ratings and review counts have been updated!")

if __name__ == "__main__":
    seed_reviews()
