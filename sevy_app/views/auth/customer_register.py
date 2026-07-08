from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sevy_app.serializers.user import CustomerRegistrationSerializer

class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "code": 200,
                "status": True,
                "message": "Customer registered successfully.",
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
