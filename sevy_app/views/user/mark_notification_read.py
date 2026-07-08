from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Notification

@api_view(['POST'])
@permission_classes([AllowAny])
def mark_notification_read(request):
    """
    Mark a specific notification as read.
    
    Body:
        notification_id (str): The ID of the notification.
    """
    try:
        notification_id = request.data.get('notification_id')

        if not notification_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing notification_id in request body.",
                "body": {}
            }, status=400)

        notification = Notification.objects.filter(notification_id=notification_id).first()
        
        if not notification:
            return Response({
                "code": 404,
                "status": False,
                "message": "Notification not found.",
                "body": {}
            }, status=404)

        if not notification.is_read:
            notification.is_read = True
            notification.save()

        return Response({
            "code": 200,
            "status": True,
            "message": "Notification marked as read successfully.",
            "body": {
                "notification_id": notification.notification_id,
                "is_read": notification.is_read
            }
        }, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
