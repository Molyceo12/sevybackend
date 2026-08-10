from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_resets')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP expires in 2 minutes
            self.expires_at = timezone.now() + timedelta(minutes=2)
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    class Meta:
        db_table = 'password_resets'
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.user.email} - Expires: {self.expires_at}"
