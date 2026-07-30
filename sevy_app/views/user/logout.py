from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing refresh_token in request body.",
            }, status=400)

        # Blacklist the refresh token so it can't be used again
        token = RefreshToken(refresh_token)
        token.blacklist()

        # Log out the specific FCM device if device_id is provided
        device_id = request.data.get('device_id')
        if device_id:
            from sevy_app.models.fcm_user import FCMUser
            FCMUser.objects.filter(device_id=device_id).update(is_loggedin=False)

        return Response({
            "code": 200,
            "status": True,
            "message": "Logged out successfully.",
        }, status=200)

    except TokenError:
        # Token already expired or invalid — treat as already logged out
        return Response({
            "code": 200,
            "status": True,
            "message": "Logged out successfully.",
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
        }, status=500)
