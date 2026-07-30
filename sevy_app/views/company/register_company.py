from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from sevy_app.serializers.user import CompanyRegistrationSerializer
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def register_company(request):
    """
    Registers a new company.
    Creates records in CustomUser, UserInfo, and Company tables via an atomic transaction.
    """
    serializer = CompanyRegistrationSerializer(data=request.data)
    
    try:
        if serializer.is_valid():
            user = serializer.save()
            
            try:
                notify_admins(
                    title="New Company Registered",
                    message=f"New rental company {user.user_info.full_names} registered and is awaiting approval.",
                    notification_type="system",
                    related_id=user.custom_id[:20]
                )
                from sevy_app.utils.email_service import send_notification_email
                send_notification_email(
                    to_email=user.email,
                    subject="Welcome to Sevy Mobility!",
                    name=user.user_info.full_names,
                    message="Thank you for registering your company with Sevy Mobility. We have received your application and our team is currently reviewing your profile and documents. We will notify you once your account has been approved.",
                    action_text="Visit Dashboard",
                    action_url="https://sevymobility.com"
                )
            except Exception as e:
                print("Notification failed, but company registered:", e)
            
            return Response({
                "code": 200,
                "status": True,
                "message": "Company registered successfully.",
                "body": {
                    "company_id": user.custom_id,
                    "email": user.email,
                    "fullname": user.user_info.full_names
                }
            }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        error_msg = str(e) + "\n" + traceback.format_exc()
        print(error_msg)
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server Error: {str(e)}",
            "body": {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
