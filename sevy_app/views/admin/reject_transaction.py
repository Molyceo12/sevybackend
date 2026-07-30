from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from sevy_app.models import Transaction, Notification, PlatformCommission, Trip, CarBooking

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_transaction(request):
    """
    Rejects a transaction.
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
            "message": f"Transaction cannot be rejected because its status is '{transaction.status}'",
            "body": {}
        }, status=400)

    # 1. Update status to cancelled for this transaction in Transaction table
    transaction.status = 'cancelled'
    transaction.completed_at = timezone.now()
    transaction.save()

    # 2. Update status to cancelled in PlatformCommission table using transaction_id
    PlatformCommission.objects.filter(transaction=transaction).update(status='cancelled')

    # Determine if the user is a company or driver
    recipient_type = "User"
    user = transaction.user

    if user:
        if hasattr(user, 'company_profile'):
            company = user.company_profile
            # Refund the balance if it was a withdrawal
            if transaction.transaction_type == 'withdrawal':
                company.balance += transaction.amount
                company.save()
            
            recipient_type = "Company"
            
            # Notify the company
            Notification.objects.create(
                user=user,
                title="Payout Rejected",
                message=f"Your transaction of {transaction.amount} {transaction.currency} has been rejected. The amount has been refunded to your balance.",
                notification_type="transaction",
                related_id=transaction.transaction_id
            )
            
            # Email the company
            if hasattr(user, 'email') and user.email:
                from sevy_app.utils.email_service import send_notification_email
                company_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Partner'
                send_notification_email(
                    to_email=user.email,
                    subject="Transaction Rejected",
                    name=company_name,
                    message=f"Your transaction of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                    details={
                        "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                        "Amount": f"{transaction.amount} {transaction.currency}",
                        "Status": "Rejected",
                        "Resolution": "The amount has been refunded to your account balance."
                    },
                    action_text="Contact Support",
                    action_url="mailto:support@sevymobility.com"
                )

        elif hasattr(user, 'driver_profile'):
            driver = user.driver_profile
            # Refund the balance if it was a withdrawal
            if transaction.transaction_type == 'withdrawal':
                driver.balance += transaction.amount
                driver.save()
                
            recipient_type = "Driver"
            
            # Notify the driver
            Notification.objects.create(
                user=user,
                title="Payout Rejected",
                message=f"Your transaction of {transaction.amount} {transaction.currency} has been rejected. The amount has been refunded to your balance.",
                notification_type="transaction",
                related_id=transaction.transaction_id
            )
            
            # Email the driver
            if hasattr(user, 'email') and user.email:
                from sevy_app.utils.email_service import send_notification_email
                driver_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Driver'
                send_notification_email(
                    to_email=user.email,
                    subject="Transaction Rejected",
                    name=driver_name,
                    message=f"Your transaction of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                    details={
                        "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                        "Amount": f"{transaction.amount} {transaction.currency}",
                        "Status": "Rejected",
                        "Resolution": "The amount has been refunded to your account balance."
                    },
                    action_text="Contact Support",
                    action_url="mailto:support@sevymobility.com"
                )

    # Notify the admin
    Notification.objects.create(
        user=request.user,
        title="Transaction Rejected",
        message=f"{recipient_type} transaction {transaction.transaction_id} for {transaction.amount} {transaction.currency} was rejected.",
        notification_type="transaction",
        related_id=transaction.transaction_id
    )

    return Response({
        "status": "success",
        "message": "Transaction rejected successfully.",
        "body": {
            "transaction_id": transaction.transaction_id,
            "new_status": transaction.status
        }
    }, status=200)
