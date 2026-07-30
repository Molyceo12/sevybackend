from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Notification

@api_view(['POST'])
@permission_classes([AllowAny])
def request_customer_approval(request):
    try:
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing booking_id.",
                "body": {}
            }, status=400)
            
        booking = CarBooking.objects.filter(booking_id=booking_id).first()
        
        if not booking:
            return Response({
                "code": 404,
                "status": False,
                "message": "Booking not found.",
                "body": {}
            }, status=404)
            
        requested_by = request.data.get('requested_by', 'company')

        if requested_by == 'driver':
            booking.driver_customer_approval = 'requestsent'
        else:
            booking.company_customer_approval = 'requestsent'
            
        booking.save()
        
        # Notify the customer to complete approval
        if booking.user:
            if requested_by == 'driver':
                notification_title = "Driver Approval Request"
                notification_msg = f"Your driver has requested your final approval for the booking: {booking.car.brand} {booking.car.name}. Please confirm to complete it."
            else:
                notification_title = "Company Approval Request"
                notification_msg = f"The rental company has requested your final approval for the booking: {booking.car.brand} {booking.car.name}. Please confirm to complete it."
            
            Notification.objects.create(
                user=booking.user,
                title=notification_title,
                message=notification_msg,
                notification_type='rental_approval',
                related_id=booking.booking_id
            )
            
            # Send FCM Notification
            from sevy_app.utils.fcm_service import send_fcm_notification
            send_fcm_notification(
                user=booking.user,
                title=notification_title,
                body=notification_msg
            )
            
            # Send Email Notification
            from sevy_app.utils.email_service import send_notification_email
            if booking.user.email:
                send_notification_email(
                    to_email=booking.user.email,
                    subject=notification_title,
                    name=booking.user.full_names if hasattr(booking.user, 'full_names') else "Customer",
                    message=f"{'Your driver' if requested_by == 'driver' else 'The rental company'} has requested your final approval for the booking below. Please open the Sevy app to complete the approval process.",
                    details=[
                        {"label": "Booking ID", "value": booking.booking_number or booking.booking_id},
                        {"label": "Car", "value": f"{booking.car.brand} {booking.car.name}"},
                    ]
                )
            
            # Schedule the Celery task to auto-accept the booking completion after 10 minutes (600 seconds)
            from sevy_app.tasks import auto_approve_booking_completion_task
            try:
                auto_approve_booking_completion_task.apply_async((booking.booking_id,), countdown=600)
                print(f"Scheduled auto-approval task for booking {booking.booking_id} in 10 minutes.")
            except Exception as celery_err:
                print(f"Failed to schedule auto-approval task: {celery_err}")
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Customer approval requested successfully.",
            "body": {
                "booking_id": booking.booking_id,
                "company_customer_approval": booking.company_customer_approval,
                "driver_customer_approval": booking.driver_customer_approval
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
