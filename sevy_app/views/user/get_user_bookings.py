from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking
import math

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_bookings(request):
    try:
        userid = request.GET.get('userid')
        
        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "userid is required.",
                "body": []
            }, status=400)
            
        bookings = CarBooking.objects.select_related(
            'user', 'car', 'driver', 'transaction'
        ).filter(user__custom_id=userid).order_by('-created_at')
        
        from sevy_app.models import SystemConfig
        config = SystemConfig.objects.first()
        driver_daily_price = float(config.driver_per_day_price) if config and config.driver_per_day_price else 20000.0
        commission_rate = (float(config.platform_commission_percentage) / 100.0) if config and config.platform_commission_percentage else 0.28

        results = []
        for booking in bookings:
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
                    "driverid": booking.driver.userid.custom_id if booking.driver.userid else None,
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
            delta = booking.end_date - booking.start_date
            duration_days = math.ceil(delta.total_seconds() / 86400)
            if duration_days <= 0:
                duration_days = 1

            car_price = float(booking.car.price_per_day) if booking.car and booking.car.price_per_day else 0.0
            car_total = car_price * duration_days
            car_commission = car_total * commission_rate

            driver_total = 0.0
            driver_commission = 0.0
            if booking.booking_type == 'with_driver':
                driver_total = driver_daily_price * duration_days
                driver_commission = driver_total * commission_rate

            subtotal = car_total + driver_total
            service_fee = car_commission + driver_commission

            payment_breakdown = {
                "duration_days": duration_days,
                "car_price_per_day": car_price,
                "car_total": car_total,
                "car_commission": car_commission,
                "driver_price_per_day": driver_daily_price if booking.booking_type == 'with_driver' else 0.0,
                "driver_total": driver_total,
                "driver_commission": driver_commission,
                "subtotal": subtotal,
                "commission_rate": commission_rate,
                "service_fee_total": service_fee,
                "final_total": subtotal + service_fee
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
                
                "start_date": booking.start_date.isoformat() if booking.start_date else None,
                "end_date": booking.end_date.isoformat() if booking.end_date else None,
                "pickup_location": booking.pickup_location,
                "dropoff_location": booking.dropoff_location,
                
                "total_price": float(booking.total_price) if booking.total_price else (subtotal + service_fee),
                
                "status": booking.status,
                "driver_status": booking.driver_status,
                "admin_approval_status": booking.admin_approval_status,
                "payment_status": booking.payment_status,
                
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
                "updated_at": booking.updated_at.isoformat() if booking.updated_at else None
            }
            results.append(body)

        return Response({
            "code": 200,
            "status": True,
            "message": "User bookings fetched successfully.",
            "body": results
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
