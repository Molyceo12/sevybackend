from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import SystemConfig

@api_view(['GET'])
@permission_classes([AllowAny])
def get_pricing_config(request):
    try:
        config = SystemConfig.objects.first()
        if not config:
            return Response({
                "code": 404,
                "status": False,
                "message": "System configuration not found.",
                "body": {}
            }, status=404)
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Pricing configuration retrieved successfully.",
            "body": {
                "driver_per_day_price": float(config.driver_per_day_price),
                "cost_per_km": float(config.cost_per_km),
                "driver_only_cost_per_km": float(config.driver_only_cost_per_km),
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
