from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
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
    from sevy_app.models import PlatformCommission
    PlatformCommission.objects.filter(transaction=transaction).update(status='completed')

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
            recipient_type = "Company"
            
            # Notify the company
            Notification.objects.create(
                user=user,
                title="Payout Approved",
                message=f"Your transaction of {transaction.amount} {transaction.currency} has been approved.",
                notification_type="transaction",
                related_id=transaction.transaction_id
            )

        elif hasattr(user, 'driver_profile'):
            driver = user.driver_profile
            # Only add to balance if it's NOT a withdrawal.
            if transaction.transaction_type != 'withdrawal':
                driver.balance += transaction.amount
                driver.bonus += transaction.amount
                driver.save()
            recipient_type = "Driver"

            # Notify the driver
            Notification.objects.create(
                user=user,
                title="Payout Approved",
                message=f"Your payout of {transaction.amount} {transaction.currency} has been approved and credited to your balance.",
                notification_type="transaction",
                related_id=transaction.transaction_id
            )

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
