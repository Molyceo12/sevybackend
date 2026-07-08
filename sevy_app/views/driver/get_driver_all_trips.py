from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Driver

@api_view(['POST'])
@permission_classes([AllowAny])
def get_driver_all_trips(request):
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
            
        # Get all trips for this driver ordered by newest first
        trips = Trip.objects.filter(driverid=driver).order_by('-created_at')
        
        body = []
        for trip in trips:
            customer_name = "Unknown"
            if trip.userid and hasattr(trip.userid, 'user_info'):
                customer_name = trip.userid.user_info.full_names
                
            body.append({
                "trip_id": trip.trip_id,
                "userid": trip.userid.custom_id if trip.userid else None,
                "customer_name": customer_name,
                "start_place_name": trip.start_place_name,
                "destination_name": trip.destination_name,
                "estimated_time": trip.estimated_time,
                "distance": f"{trip.trip_distance_km} km" if trip.trip_distance_km else "Unknown",
                "total_price": float(trip.total_price) if trip.total_price else 0.0,
                "service_type": trip.service_type,
                "status": trip.status,
                "driver_status": trip.driver_status,
                "payment_status": trip.payment_status,
                "created_at": trip.created_at
            })
            
        return Response({
            "code": 200,
            "status": True,
            "message": "All driver trips fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
