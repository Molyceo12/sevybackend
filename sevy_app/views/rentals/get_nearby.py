import math
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth surface."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')
    R = 6371.0 # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@api_view(['POST'])
@permission_classes([AllowAny])
def get_nearby_cars(request):
    try:
        lat_str = request.data.get('lat')
        long_str = request.data.get('long')

        if not lat_str or not long_str:
            return Response({
                "code": 400,
                "status": False,
                "message": "lat and long are required fields.",
                "body": []
            }, status=400)

        user_lat = float(lat_str)
        user_long = float(long_str)

        cars = Car.objects.filter(is_deleted=False)
        
        cars_data = []
        for car in cars:
            # Calculate distance
            distance_km = haversine(user_lat, user_long, car.location_lat, car.location_long)
            
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
                "distance_km": round(distance_km, 2) if distance_km != float('inf') else None,
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

        # Sort cars by distance
        # Filter out cars that don't have a valid distance first, push them to the end
        cars_data.sort(key=lambda x: (x['distance_km'] is None, x['distance_km']))
        
        # Return only top 3 nearest cars
        cars_data = cars_data[:3]

        return Response({
            "code": 200,
            "status": True,
            "message": f"Found {len(cars_data)} nearest cars.",
            "body": cars_data
        }, status=200)

    except ValueError:
        return Response({
            "code": 400,
            "status": False,
            "message": "Invalid latitude or longitude format.",
            "body": []
        }, status=400)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
