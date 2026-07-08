from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Notification, CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
def delete_notification(request):
    try:
        userid = request.data.get('userid')
        notification_id = request.data.get('notification_id')
        delete_all = request.data.get('delete_all', False)
        
        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing userid.",
                "body": {}
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid).first()
        is_admin = user and user.user_type == 'admin'

        if delete_all:
            # Delete all notifications
            if is_admin:
                deleted_count, _ = Notification.objects.filter(user__user_type='admin').delete()
            else:
                deleted_count, _ = Notification.objects.filter(user__custom_id=userid).delete()
            return Response({
                "code": 200,
                "status": True,
                "message": f"Successfully deleted {deleted_count} notifications.",
                "body": {}
            }, status=200)
            
        elif notification_id:
            # Delete single notification
            if is_admin:
                notification = Notification.objects.filter(notification_id=notification_id, user__user_type='admin').first()
            else:
                notification = Notification.objects.filter(notification_id=notification_id, user__custom_id=userid).first()
            if not notification:
                return Response({
                    "code": 404,
                    "status": False,
                    "message": "Notification not found.",
                    "body": {}
                }, status=404)
                
            notification.delete()
            return Response({
                "code": 200,
                "status": True,
                "message": "Notification deleted successfully.",
                "body": {}
            }, status=200)
            
        else:
            return Response({
                "code": 400,
                "status": False,
                "message": "Provide either notification_id or delete_all=True.",
                "body": {}
            }, status=400)
            
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
