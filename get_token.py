import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from sevy_app.models import CustomUser

user = CustomUser.objects.filter(is_superuser=True).first()
if not user:
    user = CustomUser.objects.first()

refresh = RefreshToken.for_user(user)
print("TOKEN:", str(refresh.access_token))
