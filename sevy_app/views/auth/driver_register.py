from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sevy_app.serializers.user import DriverRegistrationSerializer
from sevy_app.utils.notifications import notify_admins

class DriverRegistrationView(APIView):
    def post(self, request):
        serializer = DriverRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            notify_admins(
                title="New Driver Registered",
                message=f"New driver {user.user_info.full_names} registered and is awaiting approval.",
                notification_type="system",
                related_id=user.custom_id
            )
            
            return Response({
                "code": 200,
                "status": True,
                "message": "Driver registered successfully.",
                "body": {
                    "email": user.email,
                    "fullname": user.user_info.full_names
                }
            }, status=status.HTTP_200_OK)
            
        # Get the first error message to send back
        errors = serializer.errors
        error_messages = []
        for field, messages in errors.items():
            for message in messages:
                error_messages.append(f"{field.capitalize()}: {message}")
                
        return Response({
            "code": 400,
            "status": False,
            "message": " ".join(error_messages),
            "body": {}
        }, status=status.HTTP_400_BAD_REQUEST)
