from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from sevy_app.models.explore import Explore, ExploreCategory
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_company_explore(request):
    try:
        data = request.data
        
        company_id = data.get('company_id')
        if not company_id:
            return JsonResponse({'status': False, 'message': 'Company ID is required', 'code': status.HTTP_400_BAD_REQUEST})

        name = data.get('name')
        category_name = data.get('category')
        subcategory = data.get('subcategory')
        features = data.get('features', [])
        images = data.get('images', [])
        place_location = data.get('place_location')

        if not all([name, category_name, subcategory, place_location]):
            return JsonResponse({'status': False, 'message': 'Missing required fields', 'code': status.HTTP_400_BAD_REQUEST})

        # Fetch or create the category based on category_name
        category_obj, _ = ExploreCategory.objects.get_or_create(categoryname=category_name)

        # Create new explore item
        new_explore = Explore.objects.create(
            companyid=company_id,
            name=name,
            category=category_obj,
            subcategory=subcategory,
            features=features,
            images=images,
            place=place_location
        )

        return JsonResponse({
            'code': status.HTTP_201_CREATED,
            'status': True,
            'message': 'Place created successfully',
            'body': {
                'id': new_explore.id,
                'name': new_explore.name,
                'category': new_explore.category.categoryname if new_explore.category else '',
                'subcategory': new_explore.subcategory,
                'features': new_explore.features,
                'images': new_explore.images,
                'place_location': new_explore.place
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'status': False,
            'message': str(e)
        })
