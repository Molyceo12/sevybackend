import math
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import DriverLocation, Driver, SystemConfig

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth surface."""
    R = 6371.0 # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@api_view(['POST'])
@permission_classes([AllowAny])
def find_nearest_driver_only(request):
    try:
        start_lat_str = request.data.get('start_lat')
        start_long_str = request.data.get('start_long')
        dest_lat_str = request.data.get('dest_lat')
        dest_long_str = request.data.get('dest_long')

        if not all([start_lat_str, start_long_str, dest_lat_str, dest_long_str]):
            return Response({
                "code": 400,
                "status": False,
                "message": "start_lat, start_long, dest_lat, and dest_long are all required fields.",
                "body": {}
            }, status=400)

        start_lat = float(start_lat_str)
        start_long = float(start_long_str)
        dest_lat = float(dest_lat_str)
        dest_long = float(dest_long_str)

        # Get all driver locations
        locations = DriverLocation.objects.all()
        if not locations.exists():
            return Response({
                "code": 404,
                "status": False,
                "message": "No active drivers found.",
                "body": {}
            }, status=404)

        # nearest_driver_loc = None
        # min_distance = float('inf')

        # Find the nearest driver using Haversine formula
        # for loc in locations:
        #     # You might want to filter only approved/online drivers here in the future
        #     dist = haversine(start_lat, start_long, loc.lat, loc.long)
        #     if dist < min_distance:
        #         min_distance = dist
        #         nearest_driver_loc = loc

        # if not nearest_driver_loc:
        #      return Response({
        #         "code": 404,
        #         "status": False,
        #         "message": "No nearby drivers found.",
        #         "body": {}
        #     }, status=404)

        # Fetch driver profile details from the Driver table
        # driver_profile = Driver.objects.filter(userid=nearest_driver_loc.userid).first()

        # MOCK: Always return this specific driver for testing
        driver_profile = Driver.objects.filter(userid__custom_id="1a53c42d5499a1aad141d585").first()
        if not driver_profile:
            return Response({"code": 404, "status": False, "message": "Mock driver not found", "body": {}}, status=404)
        
        nearest_driver_loc = DriverLocation.objects.filter(userid=driver_profile.userid).first()
        min_distance = 2.5 # mock distance
        
        # Calculate actual trip distance and driver distance
        trip_distance_km = round(haversine(start_lat, start_long, dest_lat, dest_long), 2)
        driver_distance_km = round(min_distance, 2)
        
        # Fetch pricing configuration
        sys_config = SystemConfig.objects.first()
        rate_per_km = float(sys_config.driver_only_cost_per_km) if sys_config else 0.0
        choose_driver_fee_percentage = float(sys_config.choose_driver_fee_percentage) if sys_config else 0.0
        platform_commission_percentage = float(sys_config.platform_commission_percentage) if sys_config else 0.0
            
        # Calculate pricing logic
        base_price = round(trip_distance_km * rate_per_km, 2)
        trip_fee = round(base_price * (platform_commission_percentage / 100), 2)
        choose_driver_fee = round(base_price * (choose_driver_fee_percentage / 100), 2)
        total_price = round(base_price + choose_driver_fee, 2)
        
        # Format the response joining data from both tables and pricing logic
        driver_data = {
            "userid": driver_profile.userid.custom_id,
            "full_name": driver_profile.full_name if driver_profile else "Unknown",
            "phone_number": driver_profile.phone_number if driver_profile and driver_profile.phone_number else "Unknown",
            "vehicle_make_color": driver_profile.vehicle_make_color if driver_profile else "Unknown",
            "plate_number": driver_profile.plate_number if driver_profile else "Unknown",
            "driver_distance_km": driver_distance_km,
            "trip_distance_km": trip_distance_km,
            "rate_per_km": rate_per_km,
            "choose_driver_fee_percentage": choose_driver_fee_percentage,
            "platform_commission_percentage": platform_commission_percentage,
            "base_price": base_price,
            "trip_fee": trip_fee,
            "choose_driver_fee": choose_driver_fee,
            "total_price": total_price,
            "driver_lat": nearest_driver_loc.lat if nearest_driver_loc else start_lat,
            "driver_long": nearest_driver_loc.long if nearest_driver_loc else start_long,
            "place": nearest_driver_loc.place if nearest_driver_loc else "Mock Location"
        }

        return Response({
            "code": 200,
            "status": True,
            "message": "Nearest driver found successfully.",
            "body": driver_data
        }, status=200)

    except ValueError:
        return Response({
            "code": 400,
            "status": False,
            "message": "Invalid latitude or longitude format.",
            "body": {}
        }, status=400)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
