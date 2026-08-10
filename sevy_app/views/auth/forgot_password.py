from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import random
import resend

from sevy_app.models.user import CustomUser
from sevy_app.models.password_reset import PasswordReset

from rest_framework.permissions import AllowAny

class ForgotPasswordOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate 6 digit OTP
            otp_raw = str(random.randint(100000, 999999))
            
            # Format as XXX XXX
            otp_formatted = f"{otp_raw[:3]} {otp_raw[3:]}"
            
            # Update existing or create new OTP
            password_reset, created = PasswordReset.objects.update_or_create(
                user=user,
                defaults={
                    'otp': otp_raw,
                    'expires_at': None # Will be set in model save()
                }
            )
            
            # Send Email
            if hasattr(settings, 'RESEND_API_KEY') and settings.RESEND_API_KEY:
                resend.api_key = settings.RESEND_API_KEY
                
                params = {
                    "from": "Sevy Mobility <noreply@resend.dev>",
                    "to": [user.email],
                    "subject": "Your Password Reset OTP",
                    "html": f"<p>Your password reset code is: <strong>{otp_formatted}</strong></p><p>This code will expire in 2 minutes.</p>"
                }
                
                resend.Emails.send(params)
            else:
                print(f"Warning: RESEND_API_KEY not set. OTP {otp_formatted} not sent to {user.email}")
                
        except CustomUser.DoesNotExist:
            # We don't want to reveal if a user exists or not for security reasons,
            # so we just pass and return the same success message.
            pass
            
        return Response({
            "message": "If an account with that email exists, an OTP has been sent."
        }, status=status.HTTP_200_OK)
