from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car, Company

@api_view(['POST'])
@permission_classes([AllowAny])
def get_company_cars(request):
    """
    Retrieves all cars associated with a specific company ID.
    Expects company_id in the request body.
    """
    company_id = request.data.get('company_id')
    if not company_id:
        return Response({
            "status": "error",
            "message": "company_id is required in the request body",
            "body": []
        }, status=400)
    try:
        company = Company.objects.get(company_id=company_id)
        cars = Car.objects.filter(companyid=company, is_deleted=False).order_by('-created_at')
        
        cars_data = [{
            "car_id": car.car_id,
            "name": car.name,
            "brand": car.brand,
            "price_per_day": float(car.price_per_day),
            "rating": float(car.rating),
            "reviews_count": car.reviews_count,
            "capacity_seats": car.capacity_seats,
            "fuel_range": car.fuel_range,
            "images": car.images,
            "location_name": car.location_name,
            "status": car.status
        } for car in cars]

        return Response({
            "status": "success",
            "message": "Company cars retrieved successfully",
            "body": cars_data
        }, status=200)

    except Company.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Company not found",
            "body": []
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "body": []
        }, status=500)
