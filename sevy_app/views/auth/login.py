from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                "code": 400,
                "status": False,
                "message": "Email and password are required.",
                "body": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if account was deleted
        from sevy_app.models import CustomUser
        existing_user = CustomUser.objects.filter(email=email).first()
        if existing_user and existing_user.is_deleted:
            return Response({
                "code": 403,
                "status": False,
                "message": "This account has been deleted.",
                "body": {}
            }, status=status.HTTP_403_FORBIDDEN)

        # Authenticate against sevyuser (CustomUser)
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            # Get user info
            full_names = ""
            if hasattr(user, 'user_info'):
                full_names = user.user_info.full_names

            company_data = {}
            if user.user_type == 'company' and hasattr(user, 'company_profile'):
                company_data = {
                    "is_verified": user.company_profile.is_verified,
                    "is_cancelled": user.company_profile.is_cancelled,
                    "cancellation_reason": user.company_profile.cancellation_reason,
                }

            driver_data = {}
            if user.user_type == 'driver' and hasattr(user, 'driver_profile'):
                driver_data = {
                    "is_approved": user.driver_profile.is_approved,
                    "is_cancelled": user.driver_profile.is_cancelled,
                    "cancellation_reason": user.driver_profile.cancellation_reason,
                }

            return Response({
                "code": 200,
                "status": True,
                "message": "Login successful.",
                "body": {
                    "id": user.custom_id,
                    "username": full_names,
                    "usertype": user.user_type,
                    "company_status": company_data,
                    "driver_status": driver_data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "code": 401,
                "status": False,
                "message": "Invalid email or password.",
                "body": {}
            }, status=status.HTTP_401_UNAUTHORIZED)
