from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Driver

@api_view(['POST'])
@permission_classes([AllowAny])
def get_trip_details(request):
    try:
        trip_id = request.data.get('trip_id')
        if not trip_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing trip_id in request body.",
                "body": {}
            }, status=400)
            
        trip = Trip.objects.filter(trip_id=trip_id).first()
        if not trip:
            return Response({
                "code": 404,
                "status": False,
                "message": "Trip not found.",
                "body": {}
            }, status=404)

        driver_name = "Unknown"
        driver_car = "Unknown"
        driver_lat = None
        driver_long = None
        if trip.driverid:
            driver_name = trip.driverid.full_name
            if trip.service_type != 'driver_only':
                driver_car = trip.driverid.vehicle_make_color
            else:
                driver_car = None
                
            from sevy_app.models import DriverLocation
            loc = DriverLocation.objects.filter(userid=trip.driverid.userid).first()
            if loc:
                driver_lat = float(loc.lat) if loc.lat else None
                driver_long = float(loc.long) if loc.long else None

        from sevy_app.models import SystemConfig
        config = SystemConfig.objects.first()
        # You can use platform_commission_percentage or choose_driver_fee_percentage
        # We will use choose_driver_fee_percentage for the service fee calculation
        platform_commission_pct = float(config.platform_commission_percentage) if config else 28.00
        
        total_price = float(trip.total_price) if trip.total_price else 0.0
        trip_distance_km = float(trip.trip_distance_km) if trip.trip_distance_km else 0.0
        rate_per_km = float(config.driver_only_cost_per_km) if trip.service_type == 'driver_only' else float(config.cost_per_km)

        # Calculate true base fare from distance to ensure consistency
        actual_base_fare = round(trip_distance_km * rate_per_km, 2)
        if actual_base_fare > 0:
            base_fare = actual_base_fare
            choose_driver_fee = round(total_price - base_fare, 2)
            if choose_driver_fee < 0:
                choose_driver_fee = 0.0
        else:
            base_fare = total_price
            choose_driver_fee = 0.0
        
        # Platform commission deduced from the base fare
        platform_fee = round(base_fare * (platform_commission_pct / 100), 2)
        
        # Total service fee is both combined
        service_fee = round(choose_driver_fee + platform_fee, 2)
        trip_fare = round(total_price - service_fee, 2)

        body = {
            "trip_id": trip.trip_id,
            "tracking_number": trip.tracking_number or trip.trip_id,
            "userid": trip.userid.custom_id if trip.userid else None,
            "driverid": trip.driverid.userid.custom_id if trip.driverid and trip.driverid.userid else None,
            "driver_name": driver_name,
            "driver_phone": trip.driverid.phone_number if trip.driverid else None,
            "driver_car": driver_car,
            "driver_lat": driver_lat,
            "driver_long": driver_long,
            "start_place_name": trip.start_place_name,
            "start_lat": trip.start_lat,
            "start_long": trip.start_long,
            "destination_name": trip.destination_name,
            "estimated_time": trip.estimated_time,
            "distance": f"{trip.trip_distance_km} km" if trip.trip_distance_km else "Unknown",
            "payment_method": trip.payment_method,
            "service_type": trip.service_type,
            "transaction_id": trip.transaction_id,
            "trip_fare": trip_fare,
            "service_fee": service_fee,
            "total_price": total_price,
            "status": trip.status,
            "driver_status": trip.driver_status,
            "payment_status": trip.payment_status,
            "created_at": trip.created_at
        }

        return Response({
            "code": 200,
            "status": True,
            "message": "Trip details fetched successfully.",
            "body": body
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
