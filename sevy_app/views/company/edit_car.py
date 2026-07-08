from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car

@api_view(['PUT'])
@permission_classes([AllowAny])
def edit_car(request):
    try:
        data = request.data
        car_id = data.get('car_id')
        
        if not car_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "car_id is required in the request body.",
                "body": []
            }, status=400)

        car = Car.objects.filter(car_id=car_id, is_deleted=False).first()
        if not car:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car not found.",
                "body": []
            }, status=404)
        
        # Update fields if provided (excluded companyid as it's a ForeignKey)
        for field in ['name', 'brand', 'description', 'location_name', 
                      'location_lat', 'location_long', 'price_per_day', 'rating', 
                      'reviews_count', 'capacity_seats', 'engine_power', 'max_speed', 
                      'fuel_range', 'advanced_features', 'images', 'status']:
            if field in data:
                setattr(car, field, data[field])
                
        car.save()

        return Response({
            "code": 200,
            "status": True,
            "message": "Car updated successfully.",
            "body": {
                "car_id": car.car_id,
                "status": getattr(car, 'status', 'available')
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
