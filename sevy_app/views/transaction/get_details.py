from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def get_transaction_details(request):
    try:
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing transaction_id in request body.",
                "body": {}
            }, status=400)
        from django.db.models import Q
        from sevy_app.models import Trip, SystemConfig, CarBooking

        transaction = Transaction.objects.filter(transaction_id=transaction_id).first()
        if not transaction:
            transaction = Transaction.objects.filter(Q(related_id=transaction_id) | Q(tracking_number=transaction_id)).first()

        if not transaction:
            booking_obj = CarBooking.objects.filter(booking_id=transaction_id).first()
            if booking_obj and booking_obj.transaction:
                transaction = booking_obj.transaction

        if not transaction:
            return Response({
                "code": 404,
                "status": False,
                "message": "Transaction not found.",
                "body": {}
            }, status=404)
        import math
        
        driver_name = None
        driver_car = None
        distance = None
        trip_fare = 0.0
        service_fee = 0.0
        
        car_array = None
        rental_start_date = None
        rental_end_date = None
        customer_name = None
        fee_breakdown = None
        service_type = None
        booking_number = None
        trip_number = None
        
        admin_company_approval = 'none'
        admin_driver_approval = 'none'


        company_payout = float(transaction.amount or 0.0)

        # Check CarBooking lookup
        booking = None
        if transaction.related_id:
            booking = CarBooking.objects.filter(booking_id=transaction.related_id).first()
        if not booking:
            booking = CarBooking.objects.filter(transaction=transaction).first()
        if not booking and transaction_id:
            booking = CarBooking.objects.filter(booking_id=transaction_id).first()

        if booking:
            booking_number = booking.booking_number
            admin_company_approval = booking.admin_company_approval
            admin_driver_approval = booking.admin_driver_approval
            service_type = booking.booking_type
            if booking.user:
                try:
                    customer_name = booking.user.user_info.full_names
                except Exception:
                    customer_name = booking.user.custom_id
            rental_start_date = booking.start_date.isoformat() if booking.start_date else None
            rental_end_date = booking.end_date.isoformat() if booking.end_date else None
            
            if booking.car:
                car_array = {
                    "name": booking.car.name,
                    "brand": booking.car.brand,
                    "price_per_day": float(booking.car.price_per_day),
                    "images": booking.car.images
                }
            
            config = SystemConfig.objects.first()
            platform_commission_pct = float(config.platform_commission_percentage) if config else 28.00
            commission_rate = platform_commission_pct / 100.0
            driver_daily_price = float(config.driver_per_day_price) if config and config.driver_per_day_price else 20000.0
            car_price = float(booking.car.price_per_day) if booking.car and booking.car.price_per_day else 0.0
            
            delta = booking.end_date - booking.start_date
            duration_days = math.ceil(delta.total_seconds() / 86400)
            if duration_days <= 0:
                duration_days = 1
                
            company_gross = car_price * duration_days
            driver_gross = 0.0
            if booking.booking_type == 'with_driver' and booking.driver:
                driver_gross = driver_daily_price * duration_days
                driver_name = booking.driver.full_name
                
            company_commission = company_gross * commission_rate
            driver_commission = driver_gross * commission_rate
            service_fee = round(company_commission + driver_commission, 2)
            company_payout = round(company_gross - company_commission, 2)
            
            fee_breakdown = {
                "car_amount": round(company_gross, 2),
                "driver_amount": round(driver_gross, 2),
                "service_fee": service_fee,
                "company_commission": round(company_commission, 2),
                "company_payout": company_payout,
                "total_amount": float(transaction.amount) if transaction.amount else 0.0
            }
        elif transaction.related_id and transaction.transaction_type in ['trip', 'cartripbooking']:
            trip = Trip.objects.filter(trip_id=transaction.related_id).first()
            if trip:
                trip_number = trip.tracking_number
                service_type = trip.service_type
                if trip.driverid:
                    driver_name = trip.driverid.full_name
                    if trip.service_type != 'driver_only':
                        driver_car = trip.driverid.vehicle_make_color
                if trip.userid:
                    try:
                        customer_name = trip.userid.user_info.full_names
                    except Exception:
                        customer_name = trip.userid.custom_id
                distance = f"{trip.trip_distance_km} km" if trip.trip_distance_km else "Unknown"
                
                config = SystemConfig.objects.first()
                platform_commission_pct = float(config.platform_commission_percentage) if config else 28.00
                total_amount = float(transaction.amount) if transaction.amount else 0.0
                trip_distance_km = float(trip.trip_distance_km) if trip.trip_distance_km else 0.0
                rate_per_km = float(config.driver_only_cost_per_km) if trip.service_type == 'driver_only' else float(config.cost_per_km)
                
                actual_base_fare = round(trip_distance_km * rate_per_km, 2)
                if actual_base_fare > 0:
                    base_fare = actual_base_fare
                    choose_driver_fee = round(total_amount - base_fare, 2)
                    if choose_driver_fee < 0:
                        choose_driver_fee = 0.0
                else:
                    base_fare = total_amount
                    choose_driver_fee = 0.0
                
                platform_fee = round(base_fare * (platform_commission_pct / 100), 2)
                service_fee = round(choose_driver_fee + platform_fee, 2)
                trip_fare = round(total_amount - service_fee, 2)

        admin_company_approval_val = admin_company_approval if 'admin_company_approval' in locals() else 'none'
        admin_driver_approval_val = admin_driver_approval if 'admin_driver_approval' in locals() else 'none'
        company_payout_val = company_payout if 'company_payout' in locals() else float(transaction.amount or 0.0)

        body = {
            "transaction_id": transaction.transaction_id,
            "tracking_number": transaction.tracking_number or transaction.transaction_id,
            "booking_number": booking_number,
            "trip_number": trip_number,
            "userid": transaction.user.custom_id if transaction.user else None,
            "reference_number": transaction.reference_number,
            "transaction_type": transaction.transaction_type,
            "related_id": transaction.related_id,
            "amount": float(transaction.amount) if transaction.amount else 0.0,
            "currency": transaction.currency,
            "payment_method": transaction.payment_method,
            "status": transaction.status,
            "admin_company_approval": admin_company_approval_val,
            "admin_driver_approval": admin_driver_approval_val,
            "company_payout": company_payout_val,
            "description": transaction.description,
            "completed_at": transaction.completed_at,
            "created_at": transaction.created_at,
            "updated_at": transaction.updated_at,
            "driver_name": driver_name,
            "driver_car": driver_car,
            "distance": distance,
            "trip_fare": trip_fare,
            "service_fee": service_fee,
            "car_array": car_array,
            "rental_start_date": rental_start_date,
            "rental_end_date": rental_end_date,
            "customer_name": customer_name,
            "fee_breakdown": fee_breakdown,
            "service_type": service_type
        }
        
        return Response({
            "code": 200,
            "status": True,
            "message": "Transaction details fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
