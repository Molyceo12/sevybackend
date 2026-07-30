from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car, Company

@api_view(['POST'])
@permission_classes([AllowAny])
def create_car(request):
    """
    Creates a new car for a specific company.
    Expects JSON body with company_id and car details.
    """
    try:
        data = request.data
        company_id = data.get('company_id')
        
        if not company_id:
            return Response({
                "status": "error",
                "message": "company_id is required",
                "body": {}
            }, status=400)
            
        # Validate key attributes
        required_fields = ['name', 'brand', 'price_per_day', 'location_name', 'capacity_seats', 'fuel_range']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    "status": "error",
                    "message": f"'{field}' is a required attribute and cannot be empty.",
                    "body": {}
                }, status=400)
                
        # Validate images
        images = data.get('images', [])
        if not images or not isinstance(images, list) or len(images) == 0:
            return Response({
                "status": "error",
                "message": "'images' must be provided as a non-empty list of image URLs.",
                "body": {}
            }, status=400)
            
        try:
            company = Company.objects.get(company_id=company_id)
        except Company.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Company not found",
                "body": {}
            }, status=404)
        
        car = Car.objects.create(
            companyid=company,
            name=data.get('name', ''),
            brand=data.get('brand', ''),
            description=data.get('description', ''),
            location_name=data.get('location_name', ''),
            location_lat=data.get('location_lat'),
            location_long=data.get('location_long'),
            price_per_day=data.get('price_per_day', 0.0),
            capacity_seats=data.get('capacity_seats', 4),
            engine_power=data.get('engine_power', ''),
            max_speed=data.get('max_speed', ''),
            fuel_range=data.get('fuel_range', ''),
            advanced_features=data.get('advanced_features', []),
            images=data.get('images', []),
            status=data.get('status', 'available')
        )
        
        if company.company_id and company.company_id.email:
            from sevy_app.utils.email_service import send_notification_email
            company_name = company.company_id.user_info.full_names if hasattr(company.company_id, 'user_info') else 'Partner'
            send_notification_email(
                to_email=company.company_id.email,
                subject="New Car Added Successfully",
                name=company_name,
                message=f"Your new car listing for {car.brand} {car.name} has been successfully created and is now visible on the platform.",
                action_text="View Fleet",
                action_url="https://sevymobility.com/dashboard/cars"
            )


        return Response({
            "status": "success",
            "message": "Car created successfully under company",
            "body": {
                "car_id": car.car_id,
                "name": car.name,
                "status": car.status
            }
        }, status=201)

    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
