from rest_framework.decorators import api_view
from rest_framework.response import Response
from sevy_app.models import Driver

@api_view(['POST'])
def toggle_availability(request):
    try:
        user_id = request.data.get('userid')
        if not user_id:
            return Response({'status': False, 'message': 'User ID is required', 'code': 400}, status=400)

        driver = Driver.objects.filter(userid=user_id).first()
        if not driver:
            return Response({'status': False, 'message': 'Driver not found', 'code': 404}, status=404)

        driver.is_available = not driver.is_available
        driver.save()

        return Response({
            'status': True,
            'message': 'Availability updated successfully.',
            'code': 200,
            'is_available': driver.is_available
        })

    except Exception as e:
        return Response({'status': False, 'message': str(e), 'code': 500}, status=500)
