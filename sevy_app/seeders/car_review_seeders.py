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

    car_ids = [
        "f2be17e73937091b76de6691",
        "5bff0e4b92a1fd299f18353f",
        "52f9e705a8f0b19292c91419",
        "080c4fd4c7b69f48a0aab85c",
        "5015affc4d07fcf591e8606f",
        "f4623369232f02e222b72160",
        "c3335244154355af1e65339c",
        "069e52e5d388620fdb702357",
        "d9b3ad739b3ef63db35995c1"
    ]

    user_ids = [
        "16878ad4bcda75fb001dd337",
        "4ed7188ac33b121b5377e234",
        "502ca7f22310cfc095cadec6",
        "5b369477a2a60e6b33ab69cc",
        "63bd3b8e0cc337fc65e4219a",
        "7592258f976ce511f9127c16",
        "8efef24f611dd6a3f5c7fdc7",
        "b7839dc1cd41b8bf7232a87e",
        "cd6ba4aa58351fb66e2a898c"
    ]
    
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

    for car_id in car_ids:
        car = Car.objects.filter(car_id=car_id).first()
        if not car:
            print(f"Skipping car_id {car_id} as it was not found in DB.")
            continue
            
        # Give each car 2 to 4 random reviews
        num_reviews = random.randint(2, 4)
        
        # Select unique users for this car
        reviewers = random.sample(user_ids, num_reviews)
        
        for reviewer_id in reviewers:
            user = CustomUser.objects.filter(custom_id=reviewer_id).first()
            if not user:
                print(f"Skipping user_id {reviewer_id} as it was not found in DB.")
                continue
                
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

    print(f"Successfully seeded {total_created} reviews and updated Car ratings.")

if __name__ == "__main__":
    seed_reviews()
