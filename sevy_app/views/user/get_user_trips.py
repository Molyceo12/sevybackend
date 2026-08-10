from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_trips(request):
    try:
        userid = request.GET.get('userid')

        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "userid is required.",
                "body": []
            }, status=400)

        trips = Trip.objects.filter(userid__custom_id=userid).order_by('-created_at')

        trip_data = []
        for trip in trips:
            trip_data.append({
                "trip_id": trip.trip_id,
                "tracking_number": trip.tracking_number,
                "status": trip.status,
                "payment_status": trip.payment_status,
                "service_type": trip.service_type,
                "trip_type": getattr(trip, 'trip_type', 'instanttrip'),
                "driver_status": trip.driver_status,
                "total_price": str(trip.total_price),
                "estimated_time": trip.estimated_time,
                "trip_distance_km": trip.trip_distance_km,
                "payment_method": trip.payment_method,
                "start_place_name": trip.start_place_name,
                "start_lat": trip.start_lat,
                "start_long": trip.start_long,
                "destination_name": trip.destination_name,
                "destination_lat": trip.destination_lat,
                "destination_long": trip.destination_long,
                "created_at": trip.created_at.isoformat() if trip.created_at else None,
                "updated_at": trip.updated_at.isoformat() if trip.updated_at else None,
                "start_time": trip.start_time.isoformat() if trip.start_time else None,
                "driverid": trip.driverid_id,
                "approval_status": trip.approval_status,
            })

        return Response({
            "code": 200,
            "status": True,
            "message": "Trips fetched successfully.",
            "body": trip_data
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
