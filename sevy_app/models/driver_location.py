from django.db import models
from django.conf import settings

class DriverLocation(models.Model):
    userid = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_locations')
    lat = models.FloatField()
    long = models.FloatField()
    place = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'driver_locations'

    def __str__(self):
        return f"{self.userid.email} - {self.place}"
