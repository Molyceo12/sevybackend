from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from sevy_app.models.fcm_user import FCMUser

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """
    Updates or creates the FCM token for the specific device of the authenticated user.
    """
    user = request.user
    fcm_token = request.data.get('fcm_token')
    device_type = request.data.get('device_type')
    device_id = request.data.get('device_id')

    if not fcm_token or not device_id:
        return Response({'error': 'fcm_token and device_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Create or update the specific device's FCM token
    fcm_user, created = FCMUser.objects.update_or_create(
        user=user,
        device_id=device_id,
        defaults={
            'fcm_token': fcm_token,
            'device_type': device_type,
            'is_loggedin': True,
        }
    )

    return Response({'message': 'FCM token updated successfully'}, status=status.HTTP_200_OK)
