from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Count
from sevy_app.models import UserSearch

class MostSearchedPlacesView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        userid = request.data.get('userid')

        if not userid:
            return Response({
                "code": 400,
                "status": False,
                "message": "The 'userid' parameter is required in the request body.",
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

        # Aggregate UserSearch data to find most searched places for the specific user
        top_searches = list(UserSearch.objects.filter(
            user=target_user,
            search_type='place'
        ).values('search_string').annotate(
            count=Count('search_string')
        ).order_by('-count')[:5])

        results = [
            {
                "locationname": item['search_string'],
                "search_count": item['count']
            } for item in top_searches
        ]

        # If less than 4 places, backfill with global most searched places
        if len(results) < 4:
            existing_places = [item['locationname'].lower() for item in results]
            
            global_top_searches = UserSearch.objects.filter(
                search_type='place'
            ).values('search_string').annotate(
                count=Count('search_string')
            ).order_by('-count')[:10]
            
            for item in global_top_searches:
                if len(results) >= 4:
                    break
                if item['search_string'].lower() not in existing_places:
                    results.append({
                        "locationname": item['search_string'],
                        "search_count": item['count']
                    })
                    existing_places.append(item['search_string'].lower())

        # If still less than 4, backfill with hardcoded defaults
        if len(results) < 4:
            defaults = ['Kigali', 'Rubavu', 'Musanze', 'Huye']
            existing_places = [item['locationname'].lower() for item in results]
            
            for place in defaults:
                if len(results) >= 4:
                    break
                if place.lower() not in existing_places:
                    results.append({
                        "locationname": place,
                        "search_count": 0
                    })
                    existing_places.append(place.lower())

        return Response({
            "code": 200,
            "status": True,
            "message": "Most searched places retrieved successfully.",
            "body": {"results": results}
        }, status=status.HTTP_200_OK)
