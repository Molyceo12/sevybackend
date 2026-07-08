from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum
from sevy_app.models import CustomUser, Driver, Trip, CarBooking, Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def get_driver_details(request):
    try:
        userid = request.data.get('userid')
        
        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing userid in request body.",
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
            
        driver = Driver.objects.filter(userid=user).first()
        if not driver:
            return Response({
                "code": 404,
                "status": False,
                "message": "Driver profile not found.",
                "body": {}
            }, status=404)

        # Calculate metrics for completed trips and bookings
        completed_trips = Trip.objects.filter(driverid=driver, status='completed')
        completed_bookings = CarBooking.objects.filter(driver=driver, status='completed')
        
        total_trips_count = completed_trips.count()
        total_bookings_count = completed_bookings.count()
        
        # Total Earned from completed trips and bookings
        total_trip_earnings = sum([float(t.total_price) for t in completed_trips])
        total_booking_earnings = sum([float(b.total_price) for b in completed_bookings])
        total_earned = total_trip_earnings + total_booking_earnings

        # Fetch all related transactions for the driver
        all_transactions_qs = Transaction.objects.filter(user=user).order_by('-created_at')
        tx_list = []
        for tx in all_transactions_qs:
            tx_list.append({
                "transaction_id": tx.transaction_id,
                "reference_number": tx.reference_number,
                "transaction_type": tx.transaction_type,
                "related_id": tx.related_id,
                "amount": float(tx.amount),
                "currency": tx.currency,
                "payment_method": tx.payment_method,
                "status": tx.status,
                "description": tx.description,
                "created_at": tx.created_at
            })

        body = {
            "userid": user.custom_id,
            "email": user.email,
            "names": driver.full_name,
            "phone_number": driver.phone_number,
            "balance": float(driver.balance),
            "bonuses": float(driver.bonus),
            "vehicle_make_color": driver.vehicle_make_color,
            "plate_number": driver.plate_number,
            "experience_years": driver.experience_years,
            "sex": driver.sex,
            "is_approved": driver.is_approved,
            "is_available": driver.is_available,
            "total_trips": total_trips_count,
            "total_bookings": total_bookings_count,
            "total_earned": float(total_earned),
            "transactions": tx_list,
        }
        
        return Response({
            "code": 200,
            "status": True,
            "message": "Driver details fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
