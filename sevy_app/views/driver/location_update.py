from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny # Assuming drivers can update without token or with token, we use AllowAny for now
from rest_framework.response import Response
from sevy_app.models import DriverLocation
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def update_driver_location(request):
    try:
        user_id = request.data.get('userid')
        lat = request.data.get('lat')
        long = request.data.get('long')
        place = request.data.get('place')

        if not all([user_id, lat, long, place]):
            return Response({
                "code": 400,
                "status": False,
                "message": "userid, lat, long, and place are required fields.",
                "body": {}
            }, status=400)
            
        # The userid could be the custom_id or email, let's assume custom_id
        user = User.objects.filter(custom_id=user_id).first()
        if not user:
            return Response({
                "code": 404,
                "status": False,
                "message": "User not found.",
                "body": {}
            }, status=404)
            
        # Update or create the location
        driver_location, created = DriverLocation.objects.update_or_create(
            userid=user,
            defaults={
                'lat': float(lat),
                'long': float(long),
                'place': place
            }
        )
        
        return Response({
            "code": 200,
            "status": True,
            "message": "Driver location updated successfully.",
            "body": {
                "userid": user.custom_id,
                "lat": driver_location.lat,
                "long": driver_location.long,
                "place": driver_location.place
            }
        }, status=200)

    except ValueError:
        return Response({
            "code": 400,
            "status": False,
            "message": "Invalid latitude or longitude format.",
            "body": {}
        }, status=400)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
