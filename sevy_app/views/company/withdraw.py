from decimal import Decimal
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Company, Transaction, CustomUser
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def withdraw(request):
    """
    Creates a withdrawal request from a company's balance.
    Expects JSON body: {"company_id": "id", "amount": 50.00}
    Rate-limited to once every 3 minutes per company.
    """
    company_id = request.data.get('company_id')
    amount = request.data.get('amount')

    if not company_id:
        return Response({
            "status": "error",
            "message": "company_id is required in the request body",
            "body": {}
        }, status=400)

    # 3-minute Rate Limit Check
    cache_key = f"withdraw_lock_{company_id}"
    if cache.get(cache_key):
        return Response({
            "status": "error",
            "message": "You can only make a withdrawal once every 3 minutes. Please wait before trying again.",
            "body": {}
        }, status=429)

    if amount is None:
        return Response({
            "status": "error",
            "message": "amount is required in the request body",
            "body": {}
        }, status=400)

    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            return Response({
                "status": "error",
                "message": "amount must be greater than zero",
                "body": {}
            }, status=400)
    except (ValueError, TypeError):
        return Response({
            "status": "error",
            "message": "amount must be a valid number",
            "body": {}
        }, status=400)

    try:
        company = Company.objects.get(company_id=company_id)
        
        # Check for insufficient funds
        if company.balance < amount:
            return Response({
                "status": "error",
                "message": f"Insufficient balance. Current balance is {company.balance}",
                "body": {
                    "current_balance": float(company.balance)
                }
            }, status=400)

        # Deduct balance immediately (escrow)
        company.balance -= amount
        company.save()
        
        # Create the Transaction record that requires Admin approval
        transaction = Transaction.objects.create(
            user=company.user,
            related_id=company.company_id_id,
            transaction_type='withdrawal',
            amount=amount,
            currency='RWF',
            status='waitingapproval',
            description='Company withdrawal request'
        )
        
        notify_admins(
            title="New Withdrawal Request",
            message=f"Company {company.user.user_info.full_names if hasattr(company.user, 'user_info') else company.user.custom_id} requested a withdrawal of {amount} RWF.",
            notification_type="transaction",
            related_id=transaction.transaction_id
        )
        
        if company.user and company.user.email:
            from sevy_app.utils.email_service import send_notification_email
            company_name = company.user.user_info.full_names if hasattr(company.user, 'user_info') else 'Partner'
            send_notification_email(
                to_email=company.user.email,
                subject="Withdrawal Request Received",
                name=company_name,
                message=f"We have received your withdrawal request for {amount} RWF. It is currently pending admin approval and will be processed shortly.",
                action_text="View Dashboard",
                action_url="https://sevymobility.com"
            )
        
        # Set the 3-minute lock after a successful withdrawal
        cache.set(cache_key, True, timeout=180)

        return Response({
            "status": "success",
            "message": f"Successfully requested withdrawal of {amount}. Pending Admin approval.",
            "body": {
                "transaction_id": transaction.transaction_id,
                "company_id": company.company_id_id,
                "new_balance": float(company.balance),
                "status": transaction.status
            }
        }, status=200)

    except Company.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Company not found",
            "body": {}
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "body": {}
        }, status=500)
