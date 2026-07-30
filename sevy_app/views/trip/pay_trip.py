from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Transaction, Trip, CustomUser, SystemConfig, PlatformCommission, Notification
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def pay_trip(request):
    try:
        userid = request.data.get('userid')
        trip_id = request.data.get('trip_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        reference_number = request.data.get('reference_number')
        # Expect a boolean, default to True if missing
        is_default_driver = str(request.data.get('is_default_driver', 'true')).lower() == 'true'
        
        if not all([userid, trip_id, amount, payment_method]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (userid, trip_id, amount, payment_method).",
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
            
        if trip.payment_status == 'paid' or trip.transaction is not None:
            return Response({
                "code": 400,
                "status": False,
                "message": "This trip has already been paid.",
                "body": {}
            }, status=400)
            
        if not trip.driverid and is_default_driver:
            return Response({
                "code": 400,
                "status": False,
                "message": "Cannot pay for a trip that does not have a driver assigned yet.",
                "body": {}
            }, status=400)
            
        if reference_number:
            existing_transaction = Transaction.objects.filter(reference_number=reference_number).first()
            if existing_transaction:
                return Response({
                    "code": 409,
                    "status": False,
                    "message": f"A transaction with reference number '{reference_number}' already exists.",
                    "body": {}
                }, status=409)
            
        config = SystemConfig.objects.first()
        platform_commission_pct = float(config.platform_commission_percentage) if config else 28.00
        choose_driver_fee_pct = float(config.choose_driver_fee_percentage) if config else 20.00
        
        total_amount = float(amount)
        
        # Scenario Logic
        if is_default_driver:
            base_price = total_amount
            choose_driver_fee = 0.0
        else:
            # If total_amount includes a 20% markup, base_price = total_amount / 1.20
            # We round to 2 decimal places to avoid float trailing errors
            base_price = round(total_amount / (1 + (choose_driver_fee_pct / 100)), 2)
            choose_driver_fee = total_amount - base_price
            
        # Standard Commission Deducted from Driver's Base Price
        driver_outflow = base_price
        standard_commission = driver_outflow * (platform_commission_pct / 100)
        driver_net = driver_outflow - standard_commission
        
        # 1. Customer Transaction (Completed)
        customer_transaction = Transaction.objects.create(
            user=user,
            reference_number=reference_number,
            transaction_type='cartripbooking',
            related_id=trip_id,
            amount=total_amount,
            currency='RWF',
            payment_method=payment_method,
            status='completed',
            customer_approved=True
        )
        
        # 2. Driver Transaction (Wait Approval)
        if trip.driverid and trip.driverid.userid:
            driver_user = trip.driverid.userid
            Transaction.objects.create(
                user=driver_user,
                reference_number=f"{reference_number}_drv" if reference_number else None,
                transaction_type='cartripbooking',
                related_id=trip_id,
                amount=driver_net,
                currency='RWF',
                payment_method=payment_method,
                status='waitingapproval',
                customer_approved=False
            )
            
        # 3. Platform Commissions
        # Record 1: Standard Commission
        PlatformCommission.objects.create(
            source_type='cartripbooking',
            related_id=trip_id,
            user=trip.driverid.userid if trip.driverid else None,
            transaction=customer_transaction,
            total_amount=driver_outflow,
            commission_percentage=platform_commission_pct,
            commission_earned=standard_commission
        )
        
        # Record 2: Choose Driver Fee (if applicable)
        if not is_default_driver and choose_driver_fee > 0:
            PlatformCommission.objects.create(
                source_type='manual_choose_fee',
                related_id=trip_id,
                user=trip.driverid.userid if trip.driverid else None, # Record it against the driver who was chosen
                transaction=customer_transaction,
                total_amount=total_amount,
                commission_percentage=choose_driver_fee_pct,
                commission_earned=choose_driver_fee
            )
            
        # Update SystemConfig revenue pools
        if config:
            config.total_revenue = float(config.total_revenue) + standard_commission + choose_driver_fee
            config.gross_income = float(config.gross_income) + total_amount
            config.save()
            
        # Update the trip to paid
        trip.payment_status = 'paid'
        trip.transaction = customer_transaction
        trip.save()
        
        # Trigger Celery timeout task for 8 minutes (480 seconds) for the driver
        from sevy_app.tasks import trip_timeout_task
        try:
            print(f"\n:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            print(f"Trip {trip.trip_id} is paid and received in celery")
            print(f":::::::::::::::::::::::::::::::\n")
            trip_timeout_task.apply_async((trip.trip_id, 'waiting'), countdown=480)
        except Exception as celery_err:
            print(f"Failed to schedule celery task: {celery_err}")
        
        # Notifications
        Notification.objects.create(
            user=user,
            title="Payment Successful",
            message=f"Your trip payment of {total_amount} RWF was successful.",
            notification_type='transaction',
            related_id=customer_transaction.transaction_id
        )
        
        # Send FCM Notification to the Customer
        from sevy_app.utils.fcm_service import send_fcm_notification
        send_fcm_notification(
            user=user,
            title="Payment Successful",
            body=f"Your trip payment of {total_amount} RWF was successful."
        )
        
        notify_admins(
            title="Payment to Driver Successful",
            message=f"Payment to driver successfully made for trip {trip.trip_id} (Net: {driver_net} RWF).",
            notification_type='transaction',
            related_id=customer_transaction.transaction_id
        )
        
        # Send Trip Receipt Email
        from sevy_app.utils.email_service import send_customer_email, send_notification_email
        send_customer_email(
            to_email=user.email,
            subject="Your Trip Receipt",
            template_name="trip_receipt.html",
            context={
                "name": user.user_info.full_names if hasattr(user, 'user_info') else user.email,
                "trip_id": trip.tracking_number if trip.tracking_number else trip.trip_id,
                "amount": round(total_amount, 2),
                "payment_method": payment_method,
                "date": customer_transaction.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(customer_transaction, 'created_at') else ""
            }
        )
        
        # Send Assignment Email to Driver
        if trip.driverid and hasattr(trip.driverid, 'email'):
            driver_name = trip.driverid.user_info.full_names if hasattr(trip.driverid, 'user_info') else 'Driver'
            send_notification_email(
                to_email=trip.driverid.email,
                subject="New Trip Assigned!",
                name=driver_name,
                message=f"You have been assigned to a new trip (ID: {trip.tracking_number if trip.tracking_number else trip.trip_id}). The customer has successfully paid for the trip and is waiting. Please log into the app to view the trip details and start navigation.",
                details={
                    "Pickup Location": trip.pickup_location,
                    "Dropoff Location": trip.dropoff_location,
                    "Distance": f"{trip.distance_km} km" if trip.distance_km else "N/A"
                },
                action_text="View Trip",
                action_url="https://sevymobility.com"
            )
            
            # Send FCM Notification to the Driver
            send_fcm_notification(
                user=trip.driverid.userid,
                title="New Trip Assigned!",
                body="A customer has paid for a trip and is waiting for you."
            )
        
        return Response({
            "code": 201,
            "status": True,
            "message": "Trip payment processed successfully.",
            "body": {
                "transaction_id": customer_transaction.transaction_id,
                "trip_id": trip.trip_id,
                "is_default_driver": is_default_driver,
                "base_price": base_price,
                "choose_driver_fee": choose_driver_fee,
                "driver_net": driver_net,
                "total_sevy_commission": standard_commission + choose_driver_fee
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
