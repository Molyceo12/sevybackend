from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import threading
from sevy_app.models import Transaction, Notification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_transaction(request):
    """
    Approves a transaction and adds the amount to the company or driver's balance.
    Only accessible by superadmin.
    """
    if not request.user.is_superuser:
        return Response({
            "status": "error",
            "message": "Only admins can perform this action.",
            "body": {}
        }, status=403)

    transaction_id = request.data.get('transaction_id')
    if not transaction_id:
        return Response({
            "status": "error",
            "message": "transaction_id is required",
            "body": {}
        }, status=400)

    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Transaction not found",
            "body": {}
        }, status=404)

    if transaction.status not in ['waitingapproval', 'wait_approval']:
        return Response({
            "status": "error",
            "message": f"Transaction cannot be approved because its status is '{transaction.status}'",
            "body": {}
        }, status=400)

    # 1. Update status to approved for this transaction in Transaction table
    transaction.status = 'approved'
    transaction.completed_at = timezone.now()
    transaction.save()

    # 2. Update status to completed in PlatformCommission table using transaction_id
    from sevy_app.models import PlatformCommission, CarBooking, Trip
    PlatformCommission.objects.filter(transaction=transaction).update(status='completed')

    # Update adminapprovalfor if this relates to a CarBooking
    booking = None
    if transaction.related_id:
        booking = CarBooking.objects.filter(booking_id=transaction.related_id).first()
    if not booking:
        booking = CarBooking.objects.filter(transaction=transaction).first()
    if not booking and transaction_id:
        booking = CarBooking.objects.filter(booking_id=transaction_id).first()

    # Get Trip if this relates to a Trip
    trip = None
    if transaction.related_id:
        trip = Trip.objects.filter(trip_id=transaction.related_id).first()
    if not trip:
        trip = Trip.objects.filter(transaction=transaction).first()

    # Determine if the user is a company or driver and update their balance
    recipient_type = "User"
    user = transaction.user

    if user:
        if hasattr(user, 'company_profile'):
            company = user.company_profile
            # Only add to balance if it's NOT a withdrawal. 
            # (Withdrawals are deducted at request time).
            if transaction.transaction_type != 'withdrawal':
                company.balance += transaction.amount
                company.total_income = (company.total_income or 0) + transaction.amount
                company.save()
            if booking:
                booking.admin_company_approval = 'approved'
                if booking.admin_driver_approval == 'approved' or not booking.driver:
                    booking.status = 'completed'
                booking.save()

            recipient_type = "Company"
            
            # Notify the company
            booking_ref = transaction.tracking_number if getattr(transaction, 'tracking_number', None) else ""
            msg_text = f"Your booking {booking_ref} payment request has been approved.".replace("  ", " ")
            
            Notification.objects.create(
                user=user,
                title="Payout Approved",
                message=msg_text,
                notification_type="companytransaction",
                related_id=transaction.transaction_id
            )

            import threading
            
            def send_company_alerts():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    send_fcm_notification(
                        user=user,
                        title="Payout Approved",
                        body=msg_text,
                        data={"type": "companytransaction", "transaction_id": str(transaction.transaction_id)},
                        image=None
                    )
                    
                    # Email the company
                    if hasattr(user, 'email') and user.email:
                        from sevy_app.utils.email_service import send_notification_email
                        company_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Partner'
                        send_notification_email(
                            to_email=user.email,
                            subject="Transaction Approved",
                            name=company_name,
                            message=f"Your transaction of {transaction.amount} {transaction.currency} has been approved and processed.",
                            details={
                                "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                                "Amount": f"{transaction.amount} {transaction.currency}",
                                "Status": "Approved"
                            },
                            action_text="View Dashboard",
                            action_url="https://sevymobility.com"
                        )
                except Exception as e:
                    print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Error in send_company_alerts:")
                    print(f"{str(e)}")
                    print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
            
            threading.Thread(target=send_company_alerts).start()

        elif hasattr(user, 'driver_profile'):
            driver = user.driver_profile
            # Only add to balance if it's NOT a withdrawal.
            if transaction.transaction_type != 'withdrawal':
                driver.balance += transaction.amount
                driver.bonus += transaction.amount
                driver.save()
            if booking:
                booking.admin_driver_approval = 'approved'
                if booking.admin_company_approval == 'approved':
                    booking.status = 'completed'
                booking.save()
            if trip:
                trip.status = 'completed'
                trip.save()

            recipient_type = "Driver"

            # Notify the driver
            Notification.objects.create(
                user=user,
                title="Payout Approved",
                message="The completion of trip payment credited your account. Check your balance.",
                notification_type="drivertransaction",
                related_id=transaction.transaction_id
            )
            
            import threading
            def send_driver_alerts():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    send_fcm_notification(
                        user=user,
                        title="Payout Approved",
                        body="The completion of your car rental payment has been successfully credited to your account. Check your balance.",
                        data={"type": "drivertransaction", "transaction_id": str(transaction.transaction_id)},
                        image=None
                    )
                    
                    # Email the driver
                    if hasattr(user, 'email') and user.email:
                        from sevy_app.utils.email_service import send_notification_email
                        driver_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Driver'
                        send_notification_email(
                            to_email=user.email,
                            subject="Transaction Approved",
                            name=driver_name,
                            message=f"Your transaction of {transaction.amount} {transaction.currency} has been approved and processed.",
                            details={
                                "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                                "Amount": f"{transaction.amount} {transaction.currency}",
                                "Status": "Approved"
                            },
                            action_text="View Dashboard",
                            action_url="https://sevymobility.com"
                        )
                except Exception as e:
                    print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Error in send_driver_alerts:")
                    print(f"{str(e)}")
                    print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
            
            threading.Thread(target=send_driver_alerts).start()

        else:
            recipient_type = "Customer"
            
            # Notify the customer
            Notification.objects.create(
                user=user,
                title="Transaction Approved",
                message=f"Your transaction of {transaction.amount} {transaction.currency} has been approved.",
                notification_type="transaction",
                related_id=transaction.transaction_id
            )
            import threading
            def send_customer_alerts():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    send_fcm_notification(
                        user=user,
                        title="Transaction Approved",
                        body="Your transaction has been approved. Please check your balance.",
                        data={"type": "transaction", "transaction_id": str(transaction.transaction_id)}
                    )
                    
                    # Email the customer
                    if hasattr(user, 'email') and user.email:
                        from sevy_app.utils.email_service import send_notification_email
                        customer_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Customer'
                        send_notification_email(
                            to_email=user.email,
                            subject="Transaction Approved",
                            name=customer_name,
                            message=f"Your transaction of {transaction.amount} {transaction.currency} has been approved.",
                            details={
                                "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                                "Amount": f"{transaction.amount} {transaction.currency}",
                                "Status": "Approved"
                            },
                            action_text="View Dashboard",
                            action_url="https://sevymobility.com"
                        )
                except Exception as e:
                    print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Error in send_customer_alerts:")
                    print(f"{str(e)}")
                    print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
            
            threading.Thread(target=send_customer_alerts).start()

    # Notify the admin
    Notification.objects.create(
        user=request.user,
        title="Transaction Approved",
        message=f"{recipient_type} transaction {transaction.transaction_id} for {transaction.amount} {transaction.currency} was approved successfully.",
        notification_type="transaction",
        related_id=transaction.transaction_id
    )

    return Response({
        "status": "success",
        "message": "Transaction approved successfully.",
        "body": {
            "transaction_id": transaction.transaction_id,
            "new_status": transaction.status
        }
    }, status=200)
