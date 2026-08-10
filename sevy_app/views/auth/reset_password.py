from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from sevy_app.models.user import CustomUser
from sevy_app.models.password_reset import PasswordReset

from rest_framework.permissions import AllowAny

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not email or not otp or not new_password:
            return Response(
                {"error": "Email, OTP, and new password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            password_reset = PasswordReset.objects.get(user=user)
        except PasswordReset.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Clean up the provided OTP (remove spaces if user included them)
        provided_otp = str(otp).replace(" ", "")
        
        # 1. Verify OTP matches
        if password_reset.otp != provided_otp:
            return Response(
                {"error": "Invalid email or OTP"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 2. Verify OTP is not expired
        if not password_reset.is_valid():
            return Response(
                {"error": "This OTP has expired. Please request a new one."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 3. Validate the new password
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"error": e.messages}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 4. Update the user's password
        user.set_password(new_password)
        user.save()
        
        # 5. Delete the used OTP
        password_reset.delete()
        
        return Response({
            "message": "Password has been successfully updated."
        }, status=status.HTTP_200_OK)
