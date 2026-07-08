from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Driver, DriverLocation

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_drivers(request):
    try:
        # Order by balance descending (Top balance first)
        drivers = Driver.objects.all().order_by('-balance')
        locations = {loc.userid_id: loc for loc in DriverLocation.objects.all()}
        
        drivers_data = []
        for driver in drivers:
            loc = locations.get(driver.userid_id)
            
            drivers_data.append({
                "userid": driver.userid.custom_id,
                "email": driver.userid.email if driver.userid else None,
                "full_name": driver.full_name,
                "vehicle_make_color": driver.vehicle_make_color,
                "plate_number": driver.plate_number,
                "phone_number": driver.phone_number,
                "is_approved": driver.is_approved,
                "is_available": driver.is_available,
                "sex": driver.sex,
                "experience_years": driver.experience_years,
                "balance": float(driver.balance) if driver.balance else 0.0,
                "bonus": float(driver.bonus) if driver.bonus else 0.0,
                "created_at": driver.created_at,
                "current_lat": loc.lat if loc else driver.home_latitude,
                "current_long": loc.long if loc else driver.home_longitude,
                "current_place": loc.place if loc else driver.home_location_name,
            })

        return Response({
            "code": 200,
            "status": True,
            "message": "All drivers fetched successfully.",
            "body": drivers_data
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
