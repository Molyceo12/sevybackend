from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def approve_completion(request):
    try:
        userid = request.data.get('userid')
        booking_id = request.data.get('booking_id')
        
        if not all([userid, booking_id]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (userid, booking_id).",
                "body": {}
            }, status=400)
            
        booking = CarBooking.objects.filter(booking_id=booking_id).first()
        if not booking:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car booking not found.",
                "body": {}
            }, status=404)
            
        # Verify the user approving is the user who made the booking
        if booking.user.custom_id != userid:
            return Response({
                "code": 403,
                "status": False,
                "message": "Only the customer who made the booking can approve its completion.",
                "body": {}
            }, status=403)
            
        # 1. Change customer approval status only
        action = request.data.get('action', 'accept')
        requested_by = request.data.get('requested_by')
        
        new_status = 'denied' if action == 'report' else 'approved'
        
        if requested_by == 'driver':
            booking.driver_customer_approval = new_status
        elif requested_by == 'company':
            booking.company_customer_approval = new_status
        else:
            # Fallback if not specified
            booking.customer_approval_status = new_status
            booking.driver_customer_approval = new_status
            booking.company_customer_approval = new_status
        booking.save()
        
        if action == 'report':
            # Notify Admins about the reported booking
            from sevy_app.utils.notifications import notify_admins
            notify_admins(
                title="Booking Reported by Customer",
                message=f"Customer reported booking {booking.booking_number or booking.booking_id}. It needs review.",
                notification_type="support",
                related_id=booking.booking_id
            )
            
            return Response({
                "code": 200,
                "status": True,
                "message": "Booking completion request has been reported to support.",
                "body": {
                    "booking_id": booking.booking_id,
                    "status": booking.status,
                }
            }, status=200)
        
        # 2. Find associated waitingapproval payout transactions and mark them as customer_approved
        transactions = Transaction.objects.filter(
            related_id=booking_id, 
            status='waitingapproval',
            customer_approved=False
        )
        
        approved_count = 0
        for transaction in transactions:
            transaction.customer_approved = True
            transaction.save()
            approved_count += 1
            
        # 3. Notify the company and customer
        from sevy_app.models import Notification
        from sevy_app.utils.fcm_service import send_fcm_notification
        from sevy_app.utils.email_service import send_notification_email
        
        company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
        if not company_user and booking.car and booking.car.companyid:
            company_user = getattr(booking.car.companyid, 'company_id', None)
            
        notification_title = "Booking Completed"
        
        # Notify Customer
        if booking.user:
            notification_msg = f"You have approved the completion of your booking for {booking.car.brand} {booking.car.name}."
            Notification.objects.create(
                user=booking.user,
                title=notification_title,
                message=notification_msg,
                notification_type='rental',
                related_id=booking.booking_id
            )

        # Notify Company
        if company_user:
            company_msg = f"The completion of the booking for your {booking.car.brand} {booking.car.name} was approved by the customer."
            Notification.objects.create(
                user=company_user,
                title=notification_title,
                message=company_msg,
                notification_type='companybooking',
                related_id=booking.booking_id
            )
        # Notify Driver Database
        if booking.driver and booking.driver.userid:
            driver_msg = "The customer has approved the completion of the booking."
            Notification.objects.create(
                user=booking.driver.userid,
                title=notification_title,
                message=driver_msg,
                notification_type='driverbooking',
                related_id=booking.booking_id
            )
            
        # Dispatch external notifications asynchronously
        import threading
        def send_external_notifications():
            try:
                # Notify Company External
                if company_user:
                    send_fcm_notification(
                        user=company_user,
                        title=notification_title,
                        body=company_msg,
                        data={"type": "companybooking", "booking_id": str(booking.booking_id)}
                    )
                    if company_user.email:
                        send_notification_email(
                            to_email=company_user.email,
                            subject=notification_title,
                            name=company_user.full_names if hasattr(company_user, 'full_names') else "Company",
                            message="A customer has manually approved the completion of their car rental booking.",
                            details=[
                                {"label": "Booking ID", "value": booking.booking_number or booking.booking_id},
                                {"label": "Car", "value": f"{booking.car.brand} {booking.car.name}"},
                            ]
                        )
                # Notify Driver External
                if booking.driver and booking.driver.userid:
                    send_fcm_notification(
                        user=booking.driver.userid,
                        title=notification_title,
                        body=driver_msg,
                        data={"type": "driverbooking", "booking_id": str(booking.booking_id)}
                    )
                    if hasattr(booking.driver.userid, 'email') and booking.driver.userid.email:
                        send_notification_email(
                            to_email=booking.driver.userid.email,
                            subject=notification_title,
                            name=booking.driver.userid.full_names if hasattr(booking.driver.userid, 'full_names') else "Driver",
                            message="A customer has manually approved the completion of the car rental booking you were assigned to.",
                            details=[
                                {"label": "Booking ID", "value": booking.booking_number or booking.booking_id},
                                {"label": "Car", "value": f"{booking.car.brand} {booking.car.name}"},
                            ]
                        )
            except Exception as e:
                print(f"Error in send_external_notifications: {e}")
                
        threading.Thread(target=send_external_notifications).start()
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Customer approval recorded and payouts approved.",
            "body": {
                "booking_id": booking.booking_id,
                "status": booking.status,
                "payouts_approved": approved_count
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
