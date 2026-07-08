from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car, CarLike

@api_view(['GET'])
@permission_classes([AllowAny])
def check_like(request, car_id, user_id):
    try:
        car = Car.objects.filter(car_id=car_id).first()
        if not car:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car not found.",
                "body": {
                    "is_liked": False
                }
            }, status=404)

        is_liked = CarLike.objects.filter(user_id=user_id, car=car).exists()

        return Response({
            "code": 200,
            "status": True,
            "message": "Like status checked successfully.",
            "body": {
                "car_id": car_id,
                "user_id": user_id,
                "is_liked": is_liked
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
