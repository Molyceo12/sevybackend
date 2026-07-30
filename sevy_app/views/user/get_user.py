from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum
from sevy_app.models import CustomUser, UserInfo, Trip, CarBooking, Transaction, Notification

@api_view(['POST'])
@permission_classes([AllowAny])
def get_user(request):
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
            
        # Get names and phone from UserInfo
        user_info = UserInfo.objects.filter(user=user).first()
        names = user_info.full_names if user_info else ""
        phone = user_info.phone_number if user_info else ""
        
        # Get trips array where the user is the customer
        trips_qs = Trip.objects.filter(userid=user).order_by('-created_at')
        trips = []
        for trip in trips_qs:
            trips.append({
                "trip_id": trip.trip_id,
                "status": trip.status,
                "driver_status": trip.driver_status,
                "payment_status": trip.payment_status,
                "total_price": float(trip.total_price) if trip.total_price else 0.0,
                "start_place_name": trip.start_place_name,
                "destination_name": trip.destination_name,
                "created_at": trip.created_at
            })
        
        # Get bookings array
        bookings_qs = CarBooking.objects.filter(user=user).order_by('-created_at')
        bookings = []
        for booking in bookings_qs:
            bookings.append({
                "booking_id": booking.booking_id,
                "status": booking.status,
                "payment_status": booking.payment_status,
                "total_price": float(booking.total_price) if booking.total_price else 0.0,
                "car_name": f"{booking.car.brand} {booking.car.name}" if booking.car else "Unknown Car",
                "start_date": booking.start_date,
                "end_date": booking.end_date,
                "created_at": booking.created_at
            })
        
        # Get total money spent (sum of completed transactions)
        transactions = Transaction.objects.filter(user=user, status='completed')
        total_money_spent = transactions.aggregate(total=Sum('amount'))['total'] or 0.0
        

            
        body = {
            "userid": user.custom_id,
            "email": user.email,
            "user_type": user.user_type,
            "names": names,
            "total_trips": len(trips),
            "total_bookings": len(bookings),
            "total_money_spent": float(total_money_spent),
            "trips": trips,
            "bookings": bookings,
            "phone_number": phone if phone else "",
        }
        
        if user.user_type != 'customer':
            body["is_active"] = user.is_active

        # Check if user is a driver
        from sevy_app.models import Driver, Company
        driver = Driver.objects.filter(userid=user).first()
        if driver:
            if not body["phone_number"] and driver.phone_number:
                body["phone_number"] = driver.phone_number
            body["is_driver"] = True
            body["is_approved"] = driver.is_approved
            body["balance"] = float(driver.balance) if driver.balance else 0.0
            body["bonus"] = float(driver.bonus) if driver.bonus else 0.0
            
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
            body["transactions"] = tx_list
        else:
            body["is_driver"] = False
            
        company = Company.objects.filter(company_id=user).first()
        if company:
            if not body["phone_number"] and company.phone_number:
                body["phone_number"] = company.phone_number
            body["is_approved"] = company.is_verified
            body["company_type"] = company.company_type
        
        return Response({
            "code": 200,
            "status": True,
            "message": "User data fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
