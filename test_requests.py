import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from django.test import RequestFactory
from sevy_app.views.admin.get_requests import get_requests

factory = RequestFactory()
request = factory.get('/api/admin/requests/')
response = get_requests(request)
print("STATUS CODE:", response.status_code)
print("CONTENT:", response.content)
