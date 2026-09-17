import os
import requests
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

def get_driving_distance_km(start_lat, start_long, dest_lat, dest_long):
    """
    Attempts to fetch the true driving distance in km using the Mapbox Directions API.
    If it fails, it securely falls back to the Haversine formula (straight-line distance).
    """
    token = os.environ.get('MAPBOX_ACCESS_TOKEN')
    
    if token:
        try:
            url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_long},{start_lat};{dest_long},{dest_lat}?access_token={token}"
            response = requests.get(url, timeout=5) # 5 second timeout to prevent hanging the API
            
            if response.status_code == 200:
                data = response.json()
                if 'routes' in data and len(data['routes']) > 0:
                    distance_meters = data['routes'][0].get('distance', 0)
                    if distance_meters > 0:
                        return round(distance_meters / 1000.0, 2)
        except Exception as e:
            print(f"Error fetching Mapbox directions: {e}")
            
    # Fallback to haversine if API call fails or no token
    print("Falling back to Haversine formula for distance calculation")
    return round(haversine(start_long, start_lat, dest_long, dest_lat), 2)
