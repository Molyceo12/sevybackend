from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Explore

@api_view(['POST'])
@permission_classes([AllowAny])
def get_company_explore(request):
    """
    Returns all explore places for a given company_id.
    Expects company_id in the request body.
    """
    company_id = request.data.get('company_id')
    if not company_id:
        return Response({
            "code": 400,
            "status": False,
            "message": "company_id is required in the request body",
            "body": []
        }, status=400)

    try:
        places = Explore.objects.filter(companyid=company_id)
        places_data = []
        for p in places:
            places_data.append({
                "id": p.id,
                "name": p.name,
                "category": p.category.categoryname if p.category else "",
                "subcategory": p.subcategory,
                "features": p.features,
                "images": p.images,
                "place_location": p.place,
            })
        
        return Response({
            "code": 200,
            "status": True,
            "message": "Explore places retrieved successfully",
            "body": places_data
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}",
            "body": []
        }, status=500)
