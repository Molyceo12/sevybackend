from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from sevy_app.models.explore import Explore
from rest_framework import status

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_company_explore(request):
    try:
        place_id = request.data.get('place_id')
        company_id = request.data.get('company_id')

        if not place_id or not company_id:
            return JsonResponse({'status': False, 'message': 'Place ID and Company ID are required', 'code': status.HTTP_400_BAD_REQUEST})

        place = Explore.objects.filter(id=place_id, companyid=company_id).first()
        
        if not place:
            return JsonResponse({'status': False, 'message': 'Place not found or not authorized to delete', 'code': status.HTTP_404_NOT_FOUND})

        place.delete()

        return JsonResponse({
            'code': status.HTTP_200_OK,
            'status': True,
            'message': 'Place deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'status': False,
            'message': str(e)
        })
