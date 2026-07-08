from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import SystemConfig

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny]) 
def manage_system_config(request):
    try:
        config = SystemConfig.objects.first()
        if not config:
            config = SystemConfig.objects.create()

        if request.method == 'GET':
            return Response({
                "code": 200,
                "status": True,
                "message": "System config retrieved successfully.",
                "body": {
                    "driver_per_day_price": float(config.driver_per_day_price),
                    "cost_per_km": float(config.cost_per_km),
                    "driver_only_cost_per_km": float(config.driver_only_cost_per_km),
                    "choose_driver_fee_percentage": float(config.choose_driver_fee_percentage),
                    "platform_commission_percentage": float(config.platform_commission_percentage),
                    "total_revenue": float(config.total_revenue),
                    "gross_income": float(config.gross_income)
                }
            }, status=200)

        elif request.method == 'PUT':
            data = request.data
            
            if 'driver_per_day_price' in data:
                config.driver_per_day_price = data['driver_per_day_price']
            if 'cost_per_km' in data:
                config.cost_per_km = data['cost_per_km']
            if 'driver_only_cost_per_km' in data:
                config.driver_only_cost_per_km = data['driver_only_cost_per_km']
            if 'choose_driver_fee_percentage' in data:
                config.choose_driver_fee_percentage = data['choose_driver_fee_percentage']
            if 'platform_commission_percentage' in data:
                config.platform_commission_percentage = data['platform_commission_percentage']

            config.save()

            return Response({
                "code": 200,
                "status": True,
                "message": "System config updated successfully.",
                "body": {
                    "driver_per_day_price": float(config.driver_per_day_price),
                    "cost_per_km": float(config.cost_per_km),
                    "driver_only_cost_per_km": float(config.driver_only_cost_per_km),
                    "choose_driver_fee_percentage": float(config.choose_driver_fee_percentage),
                    "platform_commission_percentage": float(config.platform_commission_percentage),
                }
            }, status=200)
            
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
