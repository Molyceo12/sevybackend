from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car

@api_view(['GET'])
@permission_classes([AllowAny])
def get_car(request, car_id):
    try:
        car = Car.objects.select_related('companyid').filter(car_id=car_id).first()
        if not car:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car not found.",
                "body": []
            }, status=404)

        likes = list(car.car_likes.values_list('user_id', flat=True))
        
        # Fetch reviews
        reviews = []
        for review in car.reviews.all():
            full_name = "Anonymous User"
            try:
                if hasattr(review.user, 'user_info'):
                    full_name = review.user.user_info.full_names
            except Exception:
                pass

            reviews.append({
                "review_id": review.review_id,
                "user_id": review.user_id,
                "user_name": full_name,
                "rating": float(review.rating),
                "review_text": review.review_text,
                "created_at": review.created_at
            })

        car_data = {
            "id": car.id,
            "car_id": car.car_id,
            "companyid": car.companyid_id,
            "company": {
                "company_id": car.companyid.company_id_id,
                "host_name": car.companyid.host_name,
                "company_name": car.companyid.company_name,
                "profile_image": car.companyid.profile_image,
                "is_verified": car.companyid.is_verified,
                "phone_number": car.companyid.phone_number,
                "contact_email": car.companyid.contact_email
            } if car.companyid else None,
            "name": car.name,
            "brand": car.brand,
            "description": car.description,
            "location_name": car.location_name,
            "location_lat": car.location_lat,
            "location_long": car.location_long,
            "price_per_day": float(car.price_per_day),
            "rating": float(car.rating),
            "reviews_count": car.reviews_count,
            "capacity_seats": car.capacity_seats,
            "engine_power": car.engine_power,
            "max_speed": car.max_speed,
            "fuel_range": car.fuel_range,
            "advanced_features": car.advanced_features,
            "images": car.images,
            "likes": likes,
            "reviews": reviews,
            "created_at": car.created_at
        }

        return Response({
            "code": 200,
            "status": True,
            "message": "Car fetched successfully.",
            "body": car_data
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
