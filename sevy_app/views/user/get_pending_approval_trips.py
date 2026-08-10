from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip


@api_view(['POST'])
@permission_classes([AllowAny])
def get_pending_approval_trips(request):
    """
    Get all trips for a customer where the driver has requested completion
    approval (approval_status == 'requestsent').

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

        trips = Trip.objects.filter(
            userid__custom_id=userid,
            approval_status='requestsent'
        ).select_related(
            'driverid', 'driverid__userid', 'driverid__userid__user_info'
        ).order_by('-created_at')

        if not trips.exists():
            return Response({
                "code": 200,
                "status": True,
                "message": "No trips pending completion approval.",
                "total_count": 0,
                "body": []
            }, status=200)

        body = []
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

            body.append({
                "trip_id": trip.trip_id,
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
                "trip_type": getattr(trip, 'trip_type', 'instanttrip'),
                "status": trip.status,
                "driver_status": trip.driver_status,
                "approval_status": trip.approval_status,
                "payment_status": trip.payment_status,
                "created_at": trip.created_at.isoformat() if trip.created_at else None,
                "request_time": trip.updated_at.isoformat() if trip.updated_at else (trip.created_at.isoformat() if trip.created_at else None),
            })

        return Response({
            "code": 200,
            "status": True,
            "message": f"Found {len(body)} trip(s) pending completion approval.",
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
