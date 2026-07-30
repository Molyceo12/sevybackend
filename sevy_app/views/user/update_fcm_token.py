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

    try:
        # Create or update the specific device's FCM token
        # We lookup by device_id ONLY, so if the same device switches users, it updates the user reference instead of crashing
        fcm_user, created = FCMUser.objects.update_or_create(
            device_id=device_id,
            defaults={
                'user': user,
                'fcm_token': fcm_token,
                'device_type': device_type,
                'is_loggedin': True,
            }
        )

        print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(f"FCM Token successfully {'created' if created else 'updated'} for user: {user.email}")
        print(f"Device ID: {device_id}")
        print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")

        return Response({'message': 'FCM token updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(f"FCM TOKEN UPDATE FAILED FOR USER: {user.email}")
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
