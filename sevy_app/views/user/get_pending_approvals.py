from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, CarBooking


@api_view(['POST'])
@permission_classes([AllowAny])
def get_pending_approvals(request):
    """
    Get all pending requests for a customer.
    Includes Trips (where the driver has requested completion approval)
    and CarBookings (where the company has requested completion approval).

    Body:
        userid (str): The custom_id of the customer.
    """
    try:
        userid = request.data.get('userid')

        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing userid in request body.",
                "body": []
            }, status=400)

        # 1. Fetch Trips
        trips = Trip.objects.filter(
            userid__custom_id=userid,
            approval_status='requestsent'
        ).select_related(
            'driverid', 'driverid__userid', 'driverid__userid__user_info'
        )

        from django.db.models import Q
        
        # 2. Fetch CarBookings
        bookings = CarBooking.objects.filter(
            Q(user__custom_id=userid) &
            (Q(company_customer_approval='requestsent') | Q(driver_customer_approval='requestsent'))
        ).select_related('car', 'companyid')

        body = []

        # Process Trips
        for trip in trips:
            driver_name = "Unknown"
            driver_car = None
            driverid_str = None

            if trip.driverid:
                driver_name = trip.driverid.full_name
                driverid_str = trip.driverid.userid.custom_id if trip.driverid.userid else None
                if trip.service_type != 'driver_only':
                    driver_car = trip.driverid.vehicle_make_color
                else:
                    driver_car = None
                    
            t_updated = trip.updated_at
            t_created = trip.created_at

            body.append({
                "type": "trip",
                "id": trip.trip_id,
                "tracking_number": trip.tracking_number or trip.trip_id,
                "userid": trip.userid.custom_id if trip.userid else None,
                "driverid": driverid_str,
                "driver_name": driver_name,
                "driver_car": driver_car,
                "start_place_name": trip.start_place_name,
                "destination_name": trip.destination_name,
                "estimated_time": trip.estimated_time,
                "distance": f"{trip.trip_distance_km} km" if trip.trip_distance_km else "Unknown",
                "total_price": float(trip.total_price) if trip.total_price else 0.0,
                "payment_method": trip.payment_method,
                "service_type": trip.service_type,
                "status": trip.status,
                "driver_status": trip.driver_status,
                "approval_status": trip.approval_status,
                "payment_status": trip.payment_status,
                "created_at": t_created.isoformat() if t_created else None,
                "request_time": t_updated.isoformat() if t_updated else (t_created.isoformat() if t_created else None),
                "_sort_time": t_updated or t_created
            })

        # Process Bookings
        for booking in bookings:
            company_name = booking.companyid.company_name if booking.companyid else "Unknown Company"
            car_name = booking.car.name if booking.car else "Unknown Car"
            car_brand = booking.car.brand if booking.car else ""
            driver_name = booking.driver.full_name if booking.driver else "Unknown Driver"
            
            b_updated = booking.updated_at
            b_created = booking.created_at
            
            company_requested = booking.company_customer_approval == 'requestsent'
            driver_requested = booking.driver_customer_approval == 'requestsent'
            
            def add_booking_request(req_by):
                body.append({
                    "type": "booking",
                    "id": booking.booking_id,
                    "tracking_number": booking.booking_number or booking.booking_id,
                    "userid": booking.user.custom_id if booking.user else None,
                    "company_name": company_name,
                    "driver_name": driver_name,
                    "car_name": f"{car_brand} {car_name}".strip(),
                    "start_date": booking.start_date.isoformat() if booking.start_date else None,
                    "end_date": booking.end_date.isoformat() if booking.end_date else None,
                    "total_price": float(booking.total_price) if booking.total_price else 0.0,
                    "rental_plan": booking.rental_plan,
                    "status": booking.status,
                    "company_customer_approval": booking.company_customer_approval,
                    "driver_customer_approval": booking.driver_customer_approval,
                    "requested_by": req_by,
                    "created_at": b_created.isoformat() if b_created else None,
                    "request_time": b_updated.isoformat() if b_updated else (b_created.isoformat() if b_created else None),
                    "_sort_time": b_updated or b_created
                })

            if company_requested:
                add_booking_request("company")
            
            if driver_requested:
                add_booking_request("driver")

        # Sort: Oldest first (as requested: "sorting the ordest first")
        body.sort(key=lambda x: x['_sort_time'].timestamp() if x['_sort_time'] else 0)

        # Remove internal sort key
        for item in body:
            item.pop('_sort_time', None)

        if len(body) == 0:
            return Response({
                "code": 200,
                "status": True,
                "message": "No pending approvals.",
                "total_count": 0,
                "body": []
            }, status=200)

        return Response({
            "code": 200,
            "status": True,
            "message": f"Found {len(body)} pending approval(s).",
            "total_count": len(body),
            "body": body
        }, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
