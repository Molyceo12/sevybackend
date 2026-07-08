from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_cars(request):
    try:
        cars = Car.objects.filter(is_deleted=False)
        
        cars_data = []
        for car in cars:
            likes = list(car.car_likes.values_list('user_id', flat=True))
            cars_data.append({
                "id": car.id,
                "car_id": car.car_id,
                "companyid": car.companyid_id,
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
                "created_at": car.created_at
            })

        return Response({
            "code": 200,
            "status": True,
            "message": f"Found {len(cars_data)} cars.",
            "body": cars_data
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
