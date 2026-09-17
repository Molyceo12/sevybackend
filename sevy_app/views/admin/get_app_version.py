from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import SystemConfig

@api_view(['GET'])
@permission_classes([AllowAny]) 
def get_app_version(request):
    try:
        config = SystemConfig.objects.first()
        if not config:
            config = SystemConfig.objects.create()

        return Response({
            "code": 200,
            "status": True,
            "message": "App version retrieved successfully.",
            "body": {
                "app_version": config.app_version,
                "release_notes": config.release_notes
            }
        }, status=200)
            
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
