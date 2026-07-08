from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Notification, CustomUser


@api_view(['POST'])
@permission_classes([AllowAny])
def has_unread_notifications(request):
    """
    Checks if the user has any unread notifications.
    For admin users, checks across all admin-assigned notifications.
    Returns { "has_unread": true/false }
    """
    try:
        userid = request.data.get('userid')

        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing userid in request body.",
                "body": {"has_unread": False}
            }, status=400)

        user = CustomUser.objects.filter(custom_id=userid).first()
        if not user:
            return Response({
                "code": 404,
                "status": False,
                "message": "User not found.",
                "body": {"has_unread": False}
            }, status=404)

        if user.user_type == 'admin':
            # Admins share notifications — check any unread across all admin notifications
            has_unread = Notification.objects.filter(
                user__user_type='admin',
                is_read=False
            ).exists()
        else:
            has_unread = Notification.objects.filter(
                user=user,
                is_read=False
            ).exists()

        return Response({
            "code": 200,
            "status": True,
            "message": "Fetched unread status successfully.",
            "body": {
                "has_unread": has_unread
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {"has_unread": False}
        }, status=500)
