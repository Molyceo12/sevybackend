from decimal import Decimal
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Driver, Transaction, CustomUser
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def withdraw(request):
    """
    Creates a withdrawal request for a driver.
    Expects JSON body: {"userid": "driver_custom_id", "amount": 5000}
    Rate-limited to once every 3 minutes per driver.
    """
    userid = request.data.get('userid')
    amount = request.data.get('amount')
    payment_method = request.data.get('payment_method', 'N/A')

    if not userid:
        return Response({
            "status": "error",
            "message": "userid is required in the request body",
            "body": {}
        }, status=400)

    # 3-minute Rate Limit Check
    cache_key = f"driver_withdraw_lock_{userid}"
    if cache.get(cache_key):
        return Response({
            "status": "error",
            "message": "You can only request a withdrawal once every 3 minutes. Please wait.",
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
        driver = Driver.objects.get(userid=userid)
        
        # Check for insufficient funds
        if driver.balance < amount:
            return Response({
                "status": "error",
                "message": f"Insufficient balance. Current balance is {driver.balance}",
                "body": {
                    "current_balance": float(driver.balance)
                }
            }, status=400)

        # Deduct balance immediately to prevent double spending
        driver.balance -= amount
        driver.save()
        
        # Create the Transaction record that requires Admin approval
        transaction = Transaction.objects.create(
            user=driver.userid,
            transaction_type='withdrawal',
            amount=amount,
            currency='RWF',  # Standard currency used in the system
            status='waitingapproval',
            description='Driver withdrawal request',
            payment_method=payment_method
        )
        
        try:
            notify_admins(
                title="Withdrawal Request",
                message=f"Driver {driver.userid.user_info.full_names if hasattr(driver.userid, 'user_info') else driver.userid.custom_id} requested a withdrawal of {amount} RWF.",
                notification_type="driver_withdrawal",
                related_id=transaction.transaction_id
            )
        except Exception as e:
            print(f"\\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print(f"Driver Withdrawal Notification Error:\\n{str(e)}")
            print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\\n")
        
        if driver.userid and driver.userid.email:
            from sevy_app.utils.email_service import send_notification_email
            driver_name = driver.userid.user_info.full_names if hasattr(driver.userid, 'user_info') else 'Driver'
            send_notification_email(
                to_email=driver.userid.email,
                subject="Withdrawal Request Received",
                name=driver_name,
                message=f"We have received your withdrawal request for {amount} RWF. It is currently pending admin approval and will be processed shortly.",
                action_text="View Dashboard",
                action_url="https://sevymobility.com"
            )
        
        # Set the 3-minute lock after a successful request
        cache.set(cache_key, True, timeout=180)

        return Response({
            "status": "success",
            "message": f"Successfully requested withdrawal of {amount}. Pending Admin approval.",
            "body": {
                "transaction_id": transaction.transaction_id,
                "new_balance": float(driver.balance),
                "status": transaction.status
            }
        }, status=200)

    except Driver.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Driver not found",
            "body": {}
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "body": {}
        }, status=500)
