from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import SystemConfig

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_revenue(request):
    try:
        # Fetch the system config (which acts as a singleton)
        config = SystemConfig.objects.first()
        
        # Get total revenue, defaulting to 0.00 if config doesn't exist
        total_revenue = config.total_revenue if config else 0.00
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Total revenue retrieved successfully.",
            "total_revenue": float(total_revenue)
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
