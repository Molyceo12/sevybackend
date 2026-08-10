import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

logger = logging.getLogger(__name__)

class TokenVerificationMiddleware(MiddlewareMixin):
    """
    Custom middleware to globally verify JWT tokens for all /api/ endpoints.
    Bypasses specific open routes like login and register.
    """
    def process_request(self, request):
        import os
        env = os.environ.get('ENV', 'test')
        api_prefix = f'/api/{env}/'

        # Open routes that don't need token verification
        open_routes = [
            f'{api_prefix}login/',
            f'{api_prefix}register/',
            f'{api_prefix}register-driver/',
            f'{api_prefix}company/register/',
            f'{api_prefix}token/refresh/',
            f'{api_prefix}forgot-password/',
            f'{api_prefix}reset-password/',
        ]
        
        # We only verify requests that go to /api/
        if not request.path.startswith('/api/'):
            return None
            
        # Let open routes bypass verification
        for route in open_routes:
            if request.path.startswith(route):
                return None
                
        # Bypass for document updates since cancelled users don't have valid tokens yet
        if request.path.endswith('/update-documents/'):
            return None

        # Verify JWT Token
        auth = JWTAuthentication()
        try:
            auth_tuple = auth.authenticate(request)
            if auth_tuple is None:
                return JsonResponse({
                    "detail": "no token send",
                    "code": "token_not_provided",
                    "status": False
                }, status=401)
                
            request.user, request.auth = auth_tuple
            
        except (InvalidToken, AuthenticationFailed) as e:
            return JsonResponse({
                "detail": "token expired",
                "code": "token_not_valid",
                "status": False
            }, status=401)
            
        return None
