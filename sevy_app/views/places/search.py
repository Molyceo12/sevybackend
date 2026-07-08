from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from sevy_app.models import Location, UserSearch
import math

class PlaceSearchByTextView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        userid = request.data.get('userid')
        search_text = request.data.get('search_text')
        
        if not userid or not search_text:
            return Response({
                "code": 400,
                "status": False,
                "message": "Both 'userid' and 'search_text' are required in the request body.",
                "body": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            target_user = User.objects.get(custom_id=userid)
        except User.DoesNotExist:
            return Response({
                "code": 404,
                "status": False,
                "message": "User with the provided userid does not exist.",
                "body": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Search for locations containing the search text (case-insensitive)
        locations = Location.objects.filter(locationname__icontains=search_text)
        results = [
            {
                "locationname": loc.locationname,
                "latitude": loc.latitude,
                "longitude": loc.longitude
            } for loc in locations
        ]

        # Save the search history into UserSearch, using only the raw search string
        UserSearch.objects.create(
            user=target_user,
            search_type='place',
            search_string=search_text
        )

        return Response({
            "code": 200,
            "status": True,
            "message": "Places retrieved successfully.",
            "body": {"results": results}
        }, status=status.HTTP_200_OK)


class PlaceSearchByCoordinatesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        userid = request.data.get('userid')
        lat = request.data.get('lat')
        lng = request.data.get('lng')

        if not userid or not lat or not lng:
            return Response({
                "code": 400,
                "status": False,
                "message": "Please provide 'userid', 'lat', and 'lng' parameters.",
                "body": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            target_user = User.objects.get(custom_id=userid)
        except User.DoesNotExist:
            return Response({"error": "User with the provided userid does not exist.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        try:
            target_lat = float(lat)
            target_lng = float(lng)
        except ValueError:
            return Response({
                "code": 400,
                "status": False,
                "message": "Invalid coordinates format.",
                "body": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Simple Euclidean distance calculation to find closest points
        locations = Location.objects.all()
        results = []
        for loc in locations:
            dist = math.sqrt((loc.latitude - target_lat)**2 + (loc.longitude - target_lng)**2)
            results.append({
                "locationname": loc.locationname,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "distance": dist # lower is closer
            })

        # Sort by distance and return top 5 closest locations
        results.sort(key=lambda x: x['distance'])
        top_results = results[:5]

        # Save the search history into UserSearch, using only the raw coordinates
        UserSearch.objects.create(
            user=target_user,
            search_type='coordinates',
            search_string=f"{target_lat},{target_lng}"
        )

        return Response({
            "code": 200,
            "status": True,
            "message": "Places retrieved successfully.",
            "body": {"results": top_results}
        }, status=status.HTTP_200_OK)


class SavePlaceSelectionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        userid = request.data.get('userid')
        placeid = request.data.get('placeid')

        if not userid or not placeid:
            return Response({
                "code": 400,
                "status": False,
                "message": "Both 'userid' and 'placeid' are required.",
                "body": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            target_user = User.objects.get(custom_id=userid)
        except User.DoesNotExist:
            return Response({"error": "User with the provided userid does not exist.", "success": False}, status=status.HTTP_404_NOT_FOUND)

        # Save the place selection
        UserSearch.objects.create(
            user=target_user,
            search_type='place',
            search_string=placeid
        )

        return Response({
            "code": 200,
            "status": True,
            "message": "Place selection saved successfully.",
            "body": {}
        }, status=status.HTTP_200_OK)
