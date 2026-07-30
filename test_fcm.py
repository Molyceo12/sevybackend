import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')
django.setup()

from sevy_app.models.fcm_user import FCMUser
from sevy_app.models.user import CustomUser

users = CustomUser.objects.all()
print("All Users:")
for u in users:
    print(f" - {u.email} (ID: {u.custom_id})")

devices = FCMUser.objects.all()
print("\nAll FCM Devices:")
for d in devices:
    print(f" - User: {d.user.email} | Token: {d.fcm_token[:10]}... | LoggedIn: {d.is_loggedin}")
