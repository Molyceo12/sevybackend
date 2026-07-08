from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Driver, Transaction, PlatformCommission, SystemConfig, Notification

@api_view(['POST'])
@permission_classes([AllowAny])
def assign_driver(request):
    try:
        trip_id = request.data.get('trip_id')
        driverid_val = request.data.get('driverid')

        if not trip_id or not driverid_val:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (trip_id, driverid).",
                "body": {}
            }, status=400)

        trip = Trip.objects.filter(trip_id=trip_id).first()
        if not trip:
            return Response({
                "code": 404,
                "status": False,
                "message": "Trip not found.",
                "body": {}
            }, status=404)

        driver = Driver.objects.filter(userid__custom_id=driverid_val).first()
        if not driver:
            return Response({
                "code": 404,
                "status": False,
                "message": "Driver not found.",
                "body": {}
            }, status=404)

        if trip.driverid == driver:
            return Response({
                "code": 400,
                "status": False,
                "message": "This driver is already assigned to this trip.",
                "body": {}
            }, status=400)

        # Update the trip
        trip.driverid = driver
        trip.driver_status = 'waiting'
        trip.save()

        # Handle retroactive payout if the trip is already paid
        if trip.payment_status == 'paid':
            # Check if there is already a customer transaction for this trip
            customer_transaction = Transaction.objects.filter(
                related_id=trip_id, 
                transaction_type='cartripbooking',
                status='completed'
            ).first()

            # Make sure we haven't already created a transaction for THIS driver
            driver_transaction_exists = Transaction.objects.filter(
                user=driver.userid,
                related_id=trip_id,
                transaction_type='cartripbooking'
            ).exists()

            if customer_transaction and not driver_transaction_exists:
                config = SystemConfig.objects.first()
                platform_commission_pct = float(config.platform_commission_percentage) if config else 28.00
                choose_driver_fee_pct = float(config.choose_driver_fee_percentage) if config else 20.00
                
                total_amount = float(customer_transaction.amount)
                
                # Assume if the driver was assigned later, it was a manual driver selection with markup
                base_price = round(total_amount / (1 + (choose_driver_fee_pct / 100)), 2)
                
                driver_outflow = base_price
                standard_commission = driver_outflow * (platform_commission_pct / 100)
                driver_net = driver_outflow - standard_commission

                # Create Driver Transaction
                Transaction.objects.create(
                    user=driver.userid,
                    reference_number=f"{customer_transaction.reference_number}_drv" if customer_transaction.reference_number else None,
                    transaction_type='cartripbooking',
                    related_id=trip_id,
                    amount=driver_net,
                    currency='RWF',
                    payment_method=customer_transaction.payment_method,
                    status='waitingapproval',
                    customer_approved=False
                )

                # Update existing PlatformCommission records that were left with user=None
                PlatformCommission.objects.filter(
                    related_id=trip_id,
                    user__isnull=True
                ).update(user=driver.userid)

        # Send notification to driver
        if driver.userid:
            Notification.objects.create(
                user=driver.userid,
                title="New Manual Trip Assignment",
                message=f"You have been manually selected by a customer for a trip.",
                notification_type='trip',
                related_id=trip.trip_id
            )

        return Response({
            "code": 200,
            "status": True,
            "message": "Driver assigned successfully.",
            "body": {
                "trip_id": trip.trip_id,
                "driverid": driver.userid.custom_id if driver.userid else None,
                "driver_status": trip.driver_status
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
