import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sevy.settings")
django.setup()

from django.test import RequestFactory
from django.core.cache import cache
from sevy_app.models import Driver

driver = Driver.objects.get(userid='101cfe275fe48744d9ad9126')
driver.balance = 5000
driver.save()
cache.delete('driver_withdraw_lock_101cfe275fe48744d9ad9126')

from sevy_app.views.driver.withdraw import withdraw

factory = RequestFactory()
request = factory.post('/api/driver/withdraw/', {'userid': '101cfe275fe48744d9ad9126', 'amount': 100}, content_type='application/json')
try:
    response = withdraw(request)
    print(response.data)
except Exception as e:
    import traceback
    traceback.print_exc()
