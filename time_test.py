import os
import django
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from django.test import RequestFactory
from sevy_app.views.admin.get_requests import get_requests

# We need to simulate the token authentication or just bypass it since it's a test factory
from sevy_app.models import CustomUser
user = CustomUser.objects.filter(is_superuser=True).first()
if not user: user = CustomUser.objects.first()

factory = RequestFactory()
request = factory.get('/api/admin/requests/')
request.user = user  # Attach user directly

start = time.time()
response = get_requests(request)
end = time.time()
print(f"Time taken: {end - start} seconds")
print(f"Status Code: {response.status_code}")
