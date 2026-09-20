import math
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import DriverLocation, Driver, SystemConfig
from sevy_app.utils.mapbox_utils import get_driving_distance_km

@api_view(['POST'])
@permission_classes([AllowAny])
def find_nearest_driver(request):
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

        # MOCK: Return a driver that actually owns a car for the standard trip
        driver_profile = Driver.objects.filter(owns_car=True).first()
        if not driver_profile:
            return Response({"code": 404, "status": False, "message": "Mock driver not found", "body": {}}, status=404)
        
        nearest_driver_loc = DriverLocation.objects.filter(userid=driver_profile.userid).first()
        min_distance = 2.5 # mock distance
        
        # Calculate actual trip distance and driver distance
        trip_distance_km = get_driving_distance_km(start_lat, start_long, dest_lat, dest_long)
        driver_distance_km = round(min_distance, 2)
        
        # Fetch pricing configuration and calculate total cost
        sys_config = SystemConfig.objects.first()
        cost_per_km = float(sys_config.cost_per_km) if sys_config else 0.0
            
        total_price = round(trip_distance_km * cost_per_km, 2)
        
        # Format the response joining data from both tables
        driver_data = {
            "userid": driver_profile.userid.custom_id,
            "full_name": driver_profile.full_name if driver_profile else "Unknown",
            "phone_number": driver_profile.phone_number if driver_profile and driver_profile.phone_number else "Unknown",
            "vehicle_make_color": driver_profile.vehicle_make_color if driver_profile else "Unknown",
            "plate_number": driver_profile.plate_number if driver_profile else "Unknown",
            "driver_distance_km": driver_distance_km,
            "trip_distance_km": trip_distance_km,
            "cost_per_km": cost_per_km,
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
