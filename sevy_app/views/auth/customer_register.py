from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sevy_app.serializers.user import CustomerRegistrationSerializer

class CustomerRegistrationView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Send Welcome Email
            from sevy_app.utils.email_service import send_notification_email
            send_notification_email(
                to_email=user.email,
                subject="WELCOME TO SEVY MOBILITY!",
                name=user.user_info.full_names,
                message="Thank you for joining Sevy Mobility! We are excited to have you on board. You can now book trips, rent vehicles, and much more.",
                closing_message="We look forward to serving you soon!"
            )
            
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
