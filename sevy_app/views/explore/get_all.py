from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sevy_app.models import Explore
from sevy_app.serializers.explore import ExploreSerializer

class GetAllExploreView(APIView):
    """
    API View to retrieve all explore destinations.
    """
    def get(self, request):
        try:
            explore_locations = Explore.objects.all()
            serializer = ExploreSerializer(explore_locations, many=True)
            
            return Response({
                "code": 200,
                "status": True,
                "message": "Explore locations retrieved successfully.",
                "body": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "code": 500,
                "status": False,
                "message": f"An error occurred: {str(e)}",
                "body": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
