from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_car(request):
    car_id = request.data.get('car_id')
    if not car_id:
        return Response({
            "code": 400,
            "status": False,
            "message": "car_id is required in the request body.",
            "body": []
        }, status=400)

    try:
        car = Car.objects.filter(car_id=car_id).first()
        if not car:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car not found.",
                "body": []
            }, status=404)

        car.is_deleted = True
        car.save()

        return Response({
            "code": 200,
            "status": True,
            "message": "Car deleted successfully.",
            "body": []
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
