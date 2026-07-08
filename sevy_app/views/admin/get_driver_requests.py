from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Driver

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_driver_requests(request):
    try:
        # Fetch only drivers who are not yet approved and not cancelled
        drivers = Driver.objects.filter(is_approved=False, is_cancelled=False).order_by('-created_at')
        total_count = drivers.count()
        
        driver_data = []

        def get_file_url(file_field):
            if not file_field:
                return None
            if file_field.name.startswith('http'):
                return file_field.name
            return request.build_absolute_uri(file_field.url)

        for driver in drivers:
            driver_data.append({
                "userid": driver.userid.custom_id,
                "email": driver.userid.email,
                "company_id": driver.companyid.company_id_id if driver.companyid else None,
                "company_name": driver.companyid.company_name if driver.companyid else None,
                "full_name": driver.full_name,
                "vehicle_make_color": driver.vehicle_make_color,
                "plate_number": driver.plate_number,
                "phone_number": driver.phone_number,
                "home_location_name": driver.home_location_name,
                "home_latitude": driver.home_latitude,
                "home_longitude": driver.home_longitude,
                "is_approved": driver.is_approved,
                "balance": float(driver.balance) if driver.balance else 0.00,
                "bonus": float(driver.bonus) if driver.bonus else 0.00,
                "driving_license": get_file_url(driver.driving_license),
                "government_id": get_file_url(driver.government_id),
                "created_at": driver.created_at.isoformat() if driver.created_at else None,
                "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
            })
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Pending driver requests retrieved successfully.",
            "total_requests": total_count,
            "body": driver_data
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
