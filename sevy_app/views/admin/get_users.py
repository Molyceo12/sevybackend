from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CustomUser
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_users(request):
    try:
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)
        one_week_ago = now - timedelta(days=7)
        one_year_ago = now - timedelta(days=365)
        
        # Count all unique users
        total_users = CustomUser.objects.count()
        
        # Time-based metrics
        less_than_day = CustomUser.objects.filter(date_joined__gte=one_day_ago).count()
        less_than_week = CustomUser.objects.filter(date_joined__gte=one_week_ago).count()
        less_than_year = CustomUser.objects.filter(date_joined__gte=one_year_ago).count()
            
        return Response({
            "code": 200,
            "status": True,
            "message": "User statistics retrieved successfully.",
            "data": {
                "all_time": total_users,
                "less_than_day": less_than_day,
                "less_than_week": less_than_week,
                "less_than_year": less_than_year
            }
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
