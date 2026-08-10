from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking

@api_view(['POST'])
@permission_classes([AllowAny])
def get_booking_details(request):
    try:
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing booking_id in request body.",
                "body": {}
            }, status=400)
            
        booking = CarBooking.objects.select_related(
            'user', 'car', 'driver', 'transaction'
        ).filter(booking_id=booking_id).first()
        
        if not booking:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car booking not found.",
                "body": {}
            }, status=404)

        user_details = None
        if booking.user:
            full_names = ""
            if hasattr(booking.user, 'user_info'):
                full_names = booking.user.user_info.full_names
            user_details = {
                "userid": booking.user.custom_id,
                "email": booking.user.email,
                "full_names": full_names
            }

        driver_details = None
        if booking.driver:
            driver_details = {
                "driverid": booking.driver.userid.custom_id,
                "full_name": booking.driver.full_name,
                "phone_number": booking.driver.phone_number,
                "vehicle_make_color": booking.driver.vehicle_make_color,
                "plate_number": booking.driver.plate_number
            }

        car_details = None
        if booking.car:
            car_details = {
                "car_id": booking.car.car_id,
                "name": booking.car.name,
                "brand": booking.car.brand,
                "description": booking.car.description,
                "rating": float(booking.car.rating) if booking.car.rating else 0.0,
                "reviews_count": booking.car.reviews_count,
                "images": booking.car.images,
                "price_per_day": float(booking.car.price_per_day) if booking.car.price_per_day else 0.0
            }

        # Payment Breakdown calculation
        from sevy_app.models import SystemConfig
        import math
        config = SystemConfig.objects.first()
        driver_daily_price = float(config.driver_per_day_price) if config and config.driver_per_day_price else 20000.0
        commission_rate = (float(config.platform_commission_percentage) / 100.0) if config and config.platform_commission_percentage else 0.28

        delta = booking.end_date - booking.start_date
        duration_days = math.ceil(delta.total_seconds() / 86400)
        if duration_days <= 0:
            duration_days = 1

        car_price = float(booking.car.price_per_day) if booking.car and booking.car.price_per_day else 0.0
        
        # Use the exact total price from the table if available
        base_total = float(booking.total_price) if booking.total_price else (car_price * duration_days + (driver_daily_price * duration_days if booking.booking_type == 'with_driver' else 0.0))
        
        if booking.booking_type == 'with_driver' and (car_price + driver_daily_price) > 0:
            car_ratio = car_price / (car_price + driver_daily_price)
            driver_ratio = driver_daily_price / (car_price + driver_daily_price)
            actual_car_total = base_total * car_ratio
            actual_driver_total = base_total * driver_ratio
        else:
            actual_car_total = base_total
            actual_driver_total = 0.0

        car_commission = actual_car_total * commission_rate
        driver_commission = actual_driver_total * commission_rate

        payment_breakdown = {
            "duration_days": duration_days,
            "car_price_per_day": car_price,
            "car_total": actual_car_total - car_commission,
            "car_commission": car_commission,
            "driver_price_per_day": driver_daily_price if booking.booking_type == 'with_driver' else 0.0,
            "driver_total": actual_driver_total - driver_commission,
            "driver_commission": driver_commission,
            "subtotal": base_total,
            "commission_rate": commission_rate,
            "service_fee_total": car_commission + driver_commission,
            "final_total": base_total
        }

        body = {
            "booking_id": booking.booking_id,
            "booking_number": booking.booking_number,
            "user": user_details,
            "car": car_details,
            "driver": driver_details,
            "payment_breakdown": payment_breakdown,
            "transaction_id": booking.transaction.transaction_id if booking.transaction else None,
            
            "booking_type": booking.booking_type,
            "client_sex": booking.client_sex,
            "rental_plan": booking.rental_plan,
            
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "pickup_location": booking.pickup_location,
            "dropoff_location": booking.dropoff_location,
            
            "total_price": base_total,
            "status": booking.status,
            "driver_status": booking.driver_status,
            "admin_company_approval": booking.admin_company_approval,
            "admin_driver_approval": booking.admin_driver_approval,
            "payment_status": booking.payment_status,
            
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        }

        return Response({
            "code": 200,
            "status": True,
            "message": "Booking details fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
