from django.db import models
from django.conf import settings
from sevy_app.models.user import generate_custom_id

class FCMUser(models.Model):
    custom_id = models.CharField(max_length=50, primary_key=True, default=generate_custom_id)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='fcm_devices'
    )
    device_type = models.CharField(max_length=50, null=True, blank=True)
    device_id = models.CharField(max_length=255, unique=True)
    fcm_token = models.TextField()
    is_loggedin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fcmusers'

    def __str__(self):
        return f"{self.user.email} - {self.device_type}"
