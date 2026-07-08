from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Transaction, Trip, CustomUser

@api_view(['POST'])
@permission_classes([AllowAny])
def create_transaction(request):
    try:
        userid = request.data.get('userid')
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        reference_number = request.data.get('reference_number')
        is_pending = request.data.get('is_pending')
        is_success = request.data.get('is_success')
        
        if not all([userid, trip_id, amount, payment_method]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (userid, trip_id, amount, payment_method).",
                "body": {}
            }, status=400)
            
        if is_success is True:
            tx_status = 'waitingapproval' # Requires admin approval now
        elif is_pending is True:
            tx_status = 'pending'
        else:
            return Response({
                "code": 400,
                "status": False,
                "message": "You must provide either 'is_success': true or 'is_pending': true.",
                "body": {}
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid).first()
        if not user:
            return Response({
                "code": 404,
                "status": False,
                "message": "User not found.",
                "body": {}
            }, status=404)
            
        trip = Trip.objects.filter(trip_id=trip_id).first()
        if not trip:
            return Response({
                "code": 404,
                "status": False,
                "message": "Trip not found.",
                "body": {}
            }, status=404)
            
        if reference_number:
            existing_transaction = Transaction.objects.filter(reference_number=reference_number).first()
            if existing_transaction:
                return Response({
                    "code": 409,
                    "status": False,
                    "message": f"A transaction with reference number '{reference_number}' already exists.",
                    "body": {}
                }, status=409)
            
        transaction = Transaction.objects.create(
            user=user,
            reference_number=reference_number,
            transaction_type='trip',
            related_id=trip_id,
            amount=float(amount),
            currency='RWF',
            payment_method=payment_method,
            status=tx_status
        )
        
        # Assign the transaction foreign key
        trip.transaction = transaction
        # Even though it's waiting approval, the customer has paid
        if tx_status == 'waitingapproval':
            trip.payment_status = 'paid'
        trip.save()
        
        # Create a notification for the driver
        # Removed as transaction is pending admin approval

        # Notify the customer
        from sevy_app.models import Notification
        cust_status = "successful (pending admin approval)" if tx_status == 'waitingapproval' else "initiated"
        Notification.objects.create(
            user=trip.userid,
            title="Payment Successful" if tx_status == 'waitingapproval' else "Payment Pending",
            message=f"Your payment of {amount} RWF for the trip was {cust_status}.",
            notification_type='transaction',
            related_id=transaction.transaction_id
        )
        
        return Response({
            "code": 201,
            "status": True,
            "message": "Transaction created and trip marked as paid.",
            "body": {
                "transaction_id": transaction.transaction_id,
                "trip_id": trip.trip_id,
                "payment_status": trip.payment_status,
                "reference_number": transaction.reference_number
            }
        }, status=201)

    except ValueError:
        return Response({
            "code": 400,
            "status": False,
            "message": "Invalid amount format.",
            "body": {}
        }, status=400)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
