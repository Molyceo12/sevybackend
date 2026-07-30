import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sevy.settings")
django.setup()

from sevy_app.views.admin.reject_transaction import reject_transaction
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate

User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()

factory = RequestFactory()
request = factory.post('/api/admin/transactions/reject/', {'transaction_id': 'c9b0387787f3f12eaecd65c9'}, content_type='application/json')
force_authenticate(request, user=admin_user)

try:
    response = reject_transaction(request)
    print(response.data)
except Exception as e:
    import traceback
    traceback.print_exc()
