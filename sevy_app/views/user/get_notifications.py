from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Notification, CustomUser, CarBooking, Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def get_notifications(request):
    try:
        userid = request.data.get('userid')
        
        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing userid in request body.",
                "body": []
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid).first()
        if not user:
            return Response({
                "code": 404,
                "status": False,
                "message": "User not found.",
                "body": []
            }, status=404)
            
        if user.user_type == 'admin':
            # Admins share notifications created for any admin
            notifications = Notification.objects.filter(user__user_type='admin').order_by('-created_at')
        else:
            notifications = Notification.objects.filter(user=user).order_by('-created_at')
        
        # Collect related IDs for bulk querying to prevent N+1 query database timeouts
        booking_types = ['rental', 'booking', 'booking_cancelled']
        rental_ids = [n.related_id for n in notifications if n.notification_type in booking_types and n.related_id]
        transaction_ids = [n.related_id for n in notifications if n.notification_type == 'transaction' and n.related_id]
        
        bookings_map = {}
        if rental_ids:
            try:
                bookings = CarBooking.objects.filter(booking_id__in=rental_ids).select_related('car')
                bookings_map = {b.booking_id: b for b in bookings}
            except Exception:
                pass
                
        transactions_map = {}
        if transaction_ids:
            try:
                transactions = Transaction.objects.filter(transaction_id__in=transaction_ids)
                transactions_map = {t.transaction_id: t for t in transactions}
            except Exception:
                pass

        body = []
        for notif in notifications:
            notif_data = {
                "notification_id": notif.notification_id,
                "title": notif.title,
                "message": notif.message,
                "notification_type": notif.notification_type,
                "related_id": notif.related_id,
                "is_read": notif.is_read,
                "created_at": notif.created_at,
                "recipient_role": user.user_type,
            }
            
            if notif.notification_type in booking_types and notif.related_id:
                booking = bookings_map.get(notif.related_id)
                if booking and booking.car and booking.car.images and len(booking.car.images) > 0:
                    notif_data["image_url"] = booking.car.images[0]
            elif notif.notification_type == 'transaction' and notif.related_id:
                trx = transactions_map.get(notif.related_id)
                if trx:
                    notif_data["transaction_type"] = trx.transaction_type
            
            body.append(notif_data)
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Notifications fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
