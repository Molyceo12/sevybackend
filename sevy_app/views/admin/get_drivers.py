from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Driver
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_drivers(request):
    try:
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)
        one_week_ago = now - timedelta(days=7)
        one_year_ago = now - timedelta(days=365)

        # Fetch all drivers ordered by newest first
        drivers = Driver.objects.all().order_by('-created_at')
        total_count = drivers.count()
        
        # Calculate small statistics
        approved_count = drivers.filter(is_approved=True).count()
        pending_count = drivers.filter(is_approved=False).count()
        less_than_day = drivers.filter(created_at__gte=one_day_ago).count()
        less_than_week = drivers.filter(created_at__gte=one_week_ago).count()
        less_than_year = drivers.filter(created_at__gte=one_year_ago).count()
        
        driver_data = []
        approved_drivers = drivers.filter(is_approved=True)
        for driver in approved_drivers:
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
                "created_at": driver.created_at.isoformat() if driver.created_at else None,
                "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
            })
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Drivers retrieved successfully.",
            "statistics": {
                "total_drivers": total_count,
                "approved": approved_count,
                "pending_approval": pending_count,
                "registered_less_than_day": less_than_day,
                "registered_less_than_week": less_than_week,
                "registered_less_than_year": less_than_year
            },
            "body": driver_data
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
