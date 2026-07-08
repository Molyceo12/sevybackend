from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Company

@api_view(['POST'])
@permission_classes([AllowAny])
def search_bookings(request):
    try:
        query = request.data.get('query', '')
        company_id = request.data.get('company_id') # Optional filter
        
        if not query:
            return Response({
                "code": 400,
                "status": False,
                "message": "query string is required in the request body.",
                "body": []
            }, status=400)
            
        # Base query structure searching booking ID, status, user, and car name
        search_filter = (
            Q(booking_id__icontains=query) |
            Q(status__icontains=query) |
            Q(payment_status__icontains=query) |
            Q(pickup_location__icontains=query) |
            Q(dropoff_location__icontains=query) |
            Q(car__name__icontains=query) |
            Q(user__custom_id__icontains=query) |
            Q(driver__full_name__icontains=query)
        )
        
        # If company_id is provided, limit the search to only that company's bookings
        if company_id:
            bookings = CarBooking.objects.select_related(
                'user', 'car', 'driver', 'transaction'
            ).filter(search_filter, companyid=company_id).order_by('-created_at')
        else:
            bookings = CarBooking.objects.select_related(
                'user', 'car', 'driver', 'transaction'
            ).filter(search_filter).order_by('-created_at')

        results = []
        for booking in bookings:
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
                    "price_per_day": float(booking.car.price_per_day) if booking.car.price_per_day else 0.0
                }

            body = {
                "booking_id": booking.booking_id,
                "userid": booking.user.custom_id if booking.user else None,
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
                "payment_status": booking.payment_status,
                
                "created_at": booking.created_at,
                "updated_at": booking.updated_at
            }
            results.append(body)

        return Response({
            "code": 200,
            "status": True,
            "message": f"Found {len(results)} bookings matching '{query}'.",
            "body": results
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
