from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, CustomUser, Driver
from sevy_app.utils.notifications import notify_admins
from sevy_app.tasks import trip_timeout_task

@api_view(['POST'])
@permission_classes([AllowAny])
def create_trip(request):
    try:
        userid_val = request.data.get('userid')
        driverid_val = request.data.get('driverid')
        estimated_time = request.data.get('estimated_time')
        total_price = request.data.get('total_price')
        payment_method = request.data.get('payment_method', 'cash')
        trip_distance_km = request.data.get('trip_distance_km')
        
        start_lat = request.data.get('start_lat')
        start_long = request.data.get('start_long')
        start_place_name = request.data.get('start_place_name')
        
        destination_lat = request.data.get('destination_lat')
        destination_long = request.data.get('destination_long')
        destination_name = request.data.get('destination_name')
        
        driver_status = request.data.get('driver_status', 'waiting')
        if driver_status not in ['waiting', 'ready', 'coming']:
            return Response({
                "code": 400,
                "status": False,
                "message": "Invalid driver_status. Must be one of: waiting, ready, coming.",
                "body": {}
            }, status=400)
        
        # Basic validation for essential fields
        if not all([userid_val, estimated_time, total_price, start_lat, start_long, destination_lat, destination_long, trip_distance_km]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields.",
                "body": {}
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid_val).first()
        if not user:
             return Response({
                "code": 404,
                "status": False,
                "message": "Customer not found.",
                "body": {}
            }, status=404)
            
        driver = None
        if driverid_val:
            # Fetch the driver profile (this now correctly uses the custom ID as PK)
            driver = Driver.objects.filter(userid__custom_id=driverid_val).first()
            if not driver:
                 return Response({
                    "code": 404,
                    "status": False,
                    "message": "Driver not found.",
                    "body": {}
                }, status=404)

        # Create the trip record
        trip = Trip.objects.create(
            userid=user,
            driverid=driver,
            estimated_time=str(estimated_time),
            total_price=float(total_price),
            payment_method=payment_method,
            service_type=request.data.get('service_type', 'driver_and_car'),
            start_lat=float(start_lat),
            start_long=float(start_long),
            start_place_name=start_place_name,
            destination_lat=float(destination_lat),
            destination_long=float(destination_long),
            destination_name=destination_name,
            trip_distance_km=float(trip_distance_km) if trip_distance_km else None,
            driver_status=driver_status
        )
        
        # Create a notification for the driver
        if driver and driver.userid:
            from sevy_app.models import Notification
            Notification.objects.create(
                user=driver.userid,
                title="New Trip Request",
                message=f"You have a new trip request from {start_place_name} to {destination_name}.",
                notification_type='trip',
                related_id=trip.trip_id
            )

        # Notify the customer
        from sevy_app.models import Notification
        Notification.objects.create(
            user=trip.userid,
            title="Trip Request Created",
            message=f"Your trip request from {start_place_name} to {destination_name} is confirmed.",
            notification_type='trip',
            related_id=trip.trip_id
        )

        
        return Response({
            "code": 201,
            "status": True,
            "message": "Trip created successfully.",
            "body": {
                "trip_id": trip.trip_id,
                "status": trip.status,
                "driver_status": trip.driver_status,
                "payment_status": trip.payment_status,
                "created_at": trip.created_at,
                "total_price": trip.total_price
            }
        }, status=201)

    except ValueError:
        return Response({
            "code": 400,
            "status": False,
            "message": "Invalid number format for price or coordinates.",
            "body": {}
        }, status=400)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
