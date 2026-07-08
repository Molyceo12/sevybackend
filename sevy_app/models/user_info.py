from django.db import models
from django.conf import settings

class UserInfo(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='user_info'
    )
    full_names = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'userinfo'

    def __str__(self):
        return self.full_names
