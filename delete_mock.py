import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sevy_backend.settings")
django.setup()

from django.utils import timezone
from sevy_app.models import Driver, CustomUser

today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

drivers_to_delete = Driver.objects.filter(created_at__gte=today)
driver_count = drivers_to_delete.count()
print(f"Deleting {driver_count} drivers created today...")
for d in drivers_to_delete:
    d.delete()

users_to_delete = CustomUser.objects.filter(email__icontains='mockdriver')
user_count = users_to_delete.count()
print(f"Deleting {user_count} mock users...")
for u in users_to_delete:
    u.delete()

print("Done.")
