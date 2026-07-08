from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Transaction, CustomUser, SystemConfig, PlatformCommission, Notification
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def pay_booking(request):
    try:
        userid = request.data.get('userid')
        booking_id = request.data.get('booking_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        reference_number = request.data.get('reference_number')
        
        if not all([userid, booking_id, amount, payment_method]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (userid, booking_id, amount, payment_method).",
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
            
        booking = CarBooking.objects.filter(booking_id=booking_id).first()
        if not booking:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car booking not found.",
                "body": {}
            }, status=404)
            
        if booking.payment_status == 'paid' or booking.transaction is not None:
            return Response({
                "code": 400,
                "status": False,
                "message": "This booking has already been paid.",
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
            
        from sevy_app.models import SystemConfig, PlatformCommission
        import math
        
        config = SystemConfig.objects.first()
        platform_commission_pct = float(config.platform_commission_percentage) if config else 28.00
        commission_rate = platform_commission_pct / 100.0
        driver_daily_price = float(config.driver_per_day_price) if config and config.driver_per_day_price else 20000.0
        car_price = float(booking.car.price_per_day) if booking.car and booking.car.price_per_day else 0.0
        
        total_amount = float(amount)
        
        delta = booking.end_date - booking.start_date
        duration_days = math.ceil(delta.total_seconds() / 86400)
        if duration_days <= 0:
            duration_days = 1

        # 1. Company Gross
        company_gross = car_price * duration_days
        
        # 2. Driver Gross
        driver_gross = 0.0
        if booking.booking_type == 'with_driver' and booking.driver:
            driver_gross = driver_daily_price * duration_days
        
        # 3. System Commission
        company_commission = company_gross * commission_rate
        driver_commission = driver_gross * commission_rate
        
        # Security Check: Ensure the amount passed in the payload matches our backend math perfectly
        expected_total = company_gross + driver_gross + company_commission + driver_commission
        if abs(total_amount - expected_total) > 0.01:
            return Response({
                "code": 400,
                "status": False,
                "message": f"Payment amount mismatch. Expected {expected_total}, but got {total_amount}.",
                "body": {}
            }, status=400)
            
        # 4. Final Payouts
        company_net = company_gross - company_commission
        driver_net = driver_gross - driver_commission
        
        # 1. Customer Transaction
        customer_transaction = Transaction.objects.create(
            user=user,
            reference_number=reference_number,
            transaction_type='carbooking',
            related_id=booking_id,
            amount=total_amount,
            currency='RWF',
            payment_method=payment_method,
            status='completed',
            customer_approved=True
        )
        
        # 2. Company Transaction
        company_user = None
        # Check booking.companyid first, fallback to booking.car.companyid if it's missing
        if booking.companyid and getattr(booking.companyid, 'company_id', None):
            company_user = booking.companyid.company_id
        elif booking.car and booking.car.companyid and getattr(booking.car.companyid, 'company_id', None):
            company_user = booking.car.companyid.company_id
            
        Transaction.objects.create(
            user=company_user,
            reference_number=f"{reference_number}_comp" if reference_number else None,
            transaction_type='carbooking',
            related_id=booking_id,
            amount=company_net,
            currency='RWF',
            payment_method=payment_method,
            status='waitingapproval'
        )
        
        # 3. Driver Transaction (if applicable)
        if driver_net > 0 and booking.driver and booking.driver.userid:
            Transaction.objects.create(
                user=booking.driver.userid,
                reference_number=f"{reference_number}_drv" if reference_number else None,
                transaction_type='carbooking',
                related_id=booking_id,
                amount=driver_net,
                currency='RWF',
                payment_method=payment_method,
                status='waitingapproval',
                customer_approved=False
            )
            
        # 4. Platform Commission Table Records
        # Always record the company commission
        PlatformCommission.objects.create(
            source_type='carbooking',
            related_id=booking_id,
            user=company_user,
            transaction=customer_transaction,
            total_amount=company_gross,
            commission_percentage=platform_commission_pct,
            commission_earned=company_commission
        )
        
        # If there's a driver, record their commission separately
        if driver_gross > 0 and booking.driver and booking.driver.userid:
            PlatformCommission.objects.create(
                source_type='carbooking',
                related_id=booking_id,
                user=booking.driver.userid,
                transaction=customer_transaction,
                total_amount=driver_gross,
                commission_percentage=platform_commission_pct,
                commission_earned=driver_commission
            )
            
        # Update SystemConfig revenue pools
        if config:
            config.total_revenue = float(config.total_revenue) + company_commission + driver_commission
            config.gross_income = float(config.gross_income) + total_amount
            config.save()
        
        # Update the booking to paid and assign the transaction foreign key
        booking.payment_status = 'paid'
        booking.transaction = customer_transaction
        
        # Schedule Car Availability Tasks via Celery
        from sevy_app.tasks import mark_car_unavailable_task, mark_car_available_task, booking_timeout_task
        
        try:
            if booking.car:
                mark_car_unavailable_task.apply_async((booking.car.car_id,), eta=booking.start_date)
                mark_car_available_task.apply_async((booking.car.car_id,), eta=booking.end_date)
                print(f"Scheduled car {booking.car.car_id} availability tasks for booking {booking.booking_id}")
        except Exception as celery_err:
            print(f"Failed to schedule car availability tasks: {celery_err}")
            
        # Schedule Driver 2-minute countdown (if applicable)
        if booking.booking_type == 'with_driver' and booking.driver:
            try:
                booking_timeout_task.apply_async((booking.booking_id,), countdown=120)
                print(f"Scheduled 2-minute timeout for booking {booking.booking_id} driver.")
            except Exception as celery_err:
                print(f"Failed to schedule booking timeout task: {celery_err}")
        
        booking.save()
        
        # Create a notification for the driver if one is attached
        if booking.driver and booking.driver.userid:
            from sevy_app.models import Notification
            Notification.objects.create(
                user=booking.driver.userid,
                title="Payment Received for Booking",
                message=f"A payment of {amount} RWF has been received for the rental booking.",
                notification_type='transaction',
                related_id=customer_transaction.transaction_id
            )
            
        # Notify the customer
        from sevy_app.models import Notification
        Notification.objects.create(
            user=booking.user,
            title="Payment Successful",
            message=f"Your payment of {amount} RWF for the car booking was successful.",
            notification_type='transaction',
            related_id=customer_transaction.transaction_id
        )
        
        # Notify the company
        if company_user:
            Notification.objects.create(
                user=company_user,
                title="Payment Received",
                message=f"A payment has been successfully processed for the rental of your {booking.car.brand} {booking.car.name}.",
                notification_type='transaction',
                related_id=customer_transaction.transaction_id
            )
        
        # Notify admins
        notify_admins(
            title="Payment to Company Successful",
            message=f"Payment for booking {getattr(booking, 'booking_number', None) or booking.booking_id} successfully made.",
            notification_type='transaction',
            related_id=customer_transaction.transaction_id
        )
        
        return Response({
            "code": 201,
            "status": True,
            "message": "Transaction created and car booking marked as paid.",
            "body": {
                "transaction_id": customer_transaction.transaction_id,
                "booking_id": booking.booking_id,
                "status": booking.status,
                "payment_status": booking.payment_status,
                "reference_number": customer_transaction.reference_number
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
