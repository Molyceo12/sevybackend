from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Car, CarLike
from django.db import IntegrityError

@api_view(['POST'])
@permission_classes([AllowAny])
def like_car(request, car_id):
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "user_id is required.",
                "body": []
            }, status=400)

        car = Car.objects.filter(car_id=car_id).first()
        if not car:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car not found.",
                "body": []
            }, status=404)

        # Check if the like already exists
        existing_like = CarLike.objects.filter(user_id=user_id, car=car).first()

        if not existing_like:
            CarLike.objects.create(user_id=user_id, car=car)
            message = "Car liked successfully."
        else:
            message = "Car is already liked."

        total_likes = CarLike.objects.filter(car=car).count()

        return Response({
            "code": 200,
            "status": True,
            "message": message,
            "body": {
                "car_id": car.car_id,
                "is_liked": True,
                "total_likes": total_likes
            }
        }, status=200)

    except IntegrityError:
        return Response({
            "code": 404,
            "status": False,
            "message": "User not found. Cannot like car.",
            "body": []
        }, status=404)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
