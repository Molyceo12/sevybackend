from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from sevy_app.models.explore import Explore, ExploreCategory
from rest_framework import status

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_company_explore(request):
    try:
        data = request.data
        
        place_id = data.get('place_id')
        company_id = data.get('company_id')
        
        if not place_id or not company_id:
            return JsonResponse({'status': False, 'message': 'Place ID and Company ID are required', 'code': status.HTTP_400_BAD_REQUEST})

        place = Explore.objects.filter(id=place_id, companyid=company_id).first()
        if not place:
            return JsonResponse({'status': False, 'message': 'Place not found or not authorized to edit', 'code': status.HTTP_404_NOT_FOUND})

        name = data.get('name')
        category_name = data.get('category')
        subcategory = data.get('subcategory')
        features = data.get('features')
        images = data.get('images')
        place_location = data.get('place_location')

        if name:
            place.name = name
        if subcategory:
            place.subcategory = subcategory
        if features is not None:
            place.features = features
        if images is not None:
            place.images = images
        if place_location:
            place.place = place_location

        if category_name:
            category_obj, _ = ExploreCategory.objects.get_or_create(categoryname=category_name)
            place.category = category_obj

        place.save()

        return JsonResponse({
            'code': status.HTTP_200_OK,
            'status': True,
            'message': 'Place updated successfully',
            'body': {
                'id': place.id,
                'name': place.name,
                'category': place.category.categoryname if place.category else '',
                'subcategory': place.subcategory,
                'features': place.features,
                'images': place.images,
                'place_location': place.place
            }
        })
    except Exception as e:
        return JsonResponse({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'status': False,
            'message': str(e)
        })
