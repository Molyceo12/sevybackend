from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Company

@api_view(['POST'])
@permission_classes([AllowAny])
def get_company_bookings(request):
    try:
        company_id = request.data.get('company_id')
        if not company_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "company_id is required in the request body.",
                "body": []
            }, status=400)
            
        # Verify company exists
        company = Company.objects.filter(company_id=company_id).first()
        if not company:
            return Response({
                "code": 404,
                "status": False,
                "message": "Company not found.",
                "body": []
            }, status=404)

        # Get bookings linked directly to this company
        bookings = CarBooking.objects.select_related(
            'user', 'user__user_info', 'car', 'driver', 'transaction'
        ).filter(companyid=company_id).order_by('-created_at')

        results = []
        for booking in bookings:
            user_details = None
            if booking.user:
                full_names = ""
                phone_number = ""
                if hasattr(booking.user, 'user_info'):
                    full_names = booking.user.user_info.full_names
                    phone_number = booking.user.user_info.phone_number
                user_details = {
                    "userid": booking.user.custom_id,
                    "email": booking.user.email,
                    "full_names": full_names,
                    "phone_number": phone_number
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
                    "price_per_day": float(booking.car.price_per_day) if booking.car.price_per_day else 0.0,
                    "images": booking.car.images if booking.car.images else []
                }

            body = {
                "booking_id": booking.booking_id,
                "booking_number": getattr(booking, 'booking_number', None) or (f"BKNG-{booking.id:03d}-A-0" if getattr(booking, 'id', None) else booking.booking_id),
                "userid": booking.user.custom_id if booking.user else None,
                "user": user_details,
                "car": car_details,
                "driver": driver_details,
                "transaction_id": booking.transaction.transaction_id if booking.transaction else None,
                
                "booking_type": booking.booking_type,
                "client_sex": booking.client_sex,
                "rental_plan": booking.rental_plan,
                
                "start_date": booking.start_date,
                "end_date": booking.end_date,
                "pickup_location": booking.pickup_location,
                "dropoff_location": booking.dropoff_location,
                
                "total_price": float(booking.total_price) if booking.total_price else 0.0,
                
                "status": booking.status,
                "driver_status": booking.driver_status,
                "admin_approval_status": booking.admin_approval_status,
                "payment_status": booking.payment_status,
                
                "created_at": booking.created_at,
                "updated_at": booking.updated_at
            }
            results.append(body)

        return Response({
            "code": 200,
            "status": True,
            "message": "Company bookings fetched successfully.",
            "body": results
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
