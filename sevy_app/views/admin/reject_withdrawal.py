from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from sevy_app.models import Transaction, Notification, PlatformCommission

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_withdrawal(request):
    """
    Rejects a withdrawal transaction and refunds the user's balance.
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
        return Response({"status": "error", "message": "transaction_id is required", "body": {}}, status=400)

    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({"status": "error", "message": "Transaction not found", "body": {}}, status=404)

    if transaction.transaction_type != 'withdrawal':
        return Response({"status": "error", "message": "This endpoint is only for withdrawals.", "body": {}}, status=400)

    if transaction.status not in ['waitingapproval', 'wait_approval']:
        return Response({"status": "error", "message": f"Transaction cannot be rejected because its status is '{transaction.status}'", "body": {}}, status=400)

    # 1. Update status to cancelled
    transaction.status = 'cancelled'
    transaction.completed_at = timezone.now()
    transaction.save()

    # 2. Update status to cancelled in PlatformCommission table
    PlatformCommission.objects.filter(transaction=transaction).update(status='cancelled')

    # 3. Refund the balance
    user = transaction.user
    if user:
        if hasattr(user, 'company_profile'):
            company = user.company_profile
            company.balance = (company.balance or 0) + transaction.amount
            company.save()
        elif hasattr(user, 'driver_profile'):
            driver = user.driver_profile
            driver.balance = (driver.balance or 0) + transaction.amount
            driver.save()
            
        booking_ref = transaction.tracking_number if getattr(transaction, 'tracking_number', None) else ""
        msg_text = f"Your withdrawal request {booking_ref} has been rejected.".replace("  ", " ")
        
        user_type_str = user.user_type.lower() if hasattr(user, 'user_type') and user.user_type else ""
        if user_type_str == "driver":
            notif_type = "drivertransaction"
        elif user_type_str == "company":
            notif_type = "companytransaction"
        else:
            notif_type = "transaction"
        
        Notification.objects.create(
            user=user,
            title="Withdrawal Rejected",
            message=msg_text,
            notification_type=notif_type,
            related_id=transaction.transaction_id
        )

        import threading
        
        def send_async_alerts():
            try:
                from sevy_app.utils.fcm_service import send_fcm_notification
                send_fcm_notification(
                    user=user,
                    title="Withdrawal Rejected",
                    body=msg_text,
                    data={"type": notif_type, "transaction_id": str(transaction.transaction_id)},
                    image=None
                )
                
                if hasattr(user, 'email') and user.email:
                    from sevy_app.utils.email_service import send_notification_email
                    client_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Partner'
                    send_notification_email(
                        to_email=user.email,
                        subject="Withdrawal Rejected",
                        name=client_name,
                        message=f"Your withdrawal of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                        details={
                            "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                            "Amount": f"{transaction.amount} {transaction.currency}",
                            "Status": "Rejected",
                            "Resolution": "The amount has been refunded to your account balance."
                        },
                        action_text="Contact Support",
                        action_url="mailto:support@sevymobility.com"
                    )
            except Exception as e:
                print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                print(f"Error in reject_withdrawal background thread:")
                print(f"{str(e)}")
                print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
                
        threading.Thread(target=send_async_alerts).start()

    return Response({
        "status": "success",
        "message": "Withdrawal rejected and refunded successfully",
        "body": {
            "transaction_id": transaction.transaction_id,
            "status": transaction.status
        }
    })
