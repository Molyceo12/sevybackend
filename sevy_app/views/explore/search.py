from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from sevy_app.models import Explore

@api_view(['POST'])
@permission_classes([AllowAny])
def search_explore(request):
    try:
        query = request.data.get('query', '').strip()
        
        if not query:
            return Response({
                "code": 400,
                "status": False,
                "message": "Search query cannot be empty.",
                "body": []
            }, status=400)

        # Search across multiple fields using icontains
        results = Explore.objects.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(subcategory__icontains=query) |
            Q(place__icontains=query)
        )

        explore_data = []
        for item in results:
            explore_data.append({
                "id": item.id,
                "companyid": item.companyid,
                "name": item.name,
                "category": item.category,
                "subcategory": item.subcategory,
                "features": item.features,
                "images": item.images,
                "place": item.place
            })

        return Response({
            "code": 200,
            "status": True,
            "message": f"Found {len(explore_data)} matching results.",
            "body": explore_data
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
