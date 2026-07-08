from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Driver, CarBooking

@api_view(['POST'])
@permission_classes([AllowAny])
def get_driver_incoming_trips(request):
    """
    Get all incoming trips AND bookings for a driver.
    Returns both trips (waiting for acceptance) and bookings (pending/confirmed).
    Combined and sorted by newest first.
    """
    try:
        driverid = request.data.get('driverid')
        
        if not driverid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing driverid in request body.",
                "body": []
            }, status=400)
            
        driver = Driver.objects.filter(userid__custom_id=driverid).first()
        if not driver:
            return Response({
                "code": 404,
                "status": False,
                "message": "Driver not found.",
                "body": []
            }, status=404)
            
        # Get incoming trips (waiting, ready)
        trips = Trip.objects.filter(
            driverid=driver,
            driver_status__in=['waiting', 'ready'],
            status__in=['upcoming', 'active']
        ).select_related('userid')
        
        # Get incoming bookings (pending only - waiting for action)
        bookings = CarBooking.objects.filter(
            driver=driver,
            status='pending',
            driver_status='waiting'
        ).select_related('user', 'car', 'companyid')
        
        body = []
        
        # Add trips to body
        for trip in trips:
            customer_name = "Unknown"
            if trip.userid and hasattr(trip.userid, 'user_info'):
                customer_name = trip.userid.user_info.full_names
                
            body.append({
                "type": "trip",
                "trip_id": trip.trip_id,
                "tracking_number": trip.tracking_number,
                "userid": trip.userid.custom_id if trip.userid else None,
                "customer_name": customer_name,
                "start_place_name": trip.start_place_name,
                "destination_name": trip.destination_name,
                "estimated_time": trip.estimated_time,
                "distance": f"{trip.trip_distance_km} km" if trip.trip_distance_km else "Unknown",
                "total_price": float(trip.total_price) if trip.total_price else 0.0,
                "status": trip.status,
                "driver_status": trip.driver_status,
                "payment_status": trip.payment_status,
                "service_type": trip.service_type,
                "created_at": trip.created_at
            })
        
        # Add bookings to body
        for booking in bookings:
            customer_name = "Unknown"
            if booking.user and hasattr(booking.user, 'user_info'):
                customer_name = booking.user.user_info.full_names
            
            car_details = None
            if booking.car:
                car_details = {
                    "car_id": booking.car.car_id,
                    "name": booking.car.name,
                    "brand": booking.car.brand
                }
            
            company_details = None
            if booking.companyid:
                company_details = {
                    "company_id": booking.companyid.company_id.custom_id if booking.companyid.company_id else None,
                    "company_name": booking.companyid.company_name
                }
                
            body.append({
                "type": "booking",
                "booking_id": booking.booking_id,
                "booking_number": booking.booking_number,
                "userid": booking.user.custom_id if booking.user else None,
                "customer_name": customer_name,
                "car": car_details,
                "company": company_details,
                "booking_type": booking.booking_type,
                "rental_plan": booking.rental_plan,
                "start_date": booking.start_date,
                "end_date": booking.end_date,
                "pickup_location": booking.pickup_location,
                "dropoff_location": booking.dropoff_location,
                "total_price": float(booking.total_price) if booking.total_price else 0.0,
                "status": booking.status,
                "driver_status": booking.driver_status,
                "payment_status": booking.payment_status,
                "created_at": booking.created_at
            })
        
        # Sort by created_at descending (newest first)
        body.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Convert datetime to ISO format string for JSON serialization
        for item in body:
            if item['created_at']:
                item['created_at'] = item['created_at'].isoformat()
            if item['type'] == 'booking':
                if item.get('start_date'):
                    item['start_date'] = item['start_date'].isoformat()
                if item.get('end_date'):
                    item['end_date'] = item['end_date'].isoformat()
            
        return Response({
            "code": 200,
            "status": True,
            "message": f"Incoming requests fetched successfully. Found {len(trips)} trip(s) and {len(bookings)} booking(s).",
            "total_count": len(body),
            "trips_count": len(trips),
            "bookings_count": len(bookings),
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
