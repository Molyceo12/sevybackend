from django.db import models
from django.conf import settings
import secrets

def generate_search_id():
    return secrets.token_hex(12)

class UserSearch(models.Model):
    SEARCH_TYPE_CHOICES = (
        ('place', 'Place'),
        
    )

    id = models.CharField(max_length=50, primary_key=True, default=generate_search_id, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='searches')
    search_type = models.CharField(max_length=50, choices=SEARCH_TYPE_CHOICES, default='place')
    search_string = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usersearch'

    def __str__(self):
        return f"{self.user.email} - {self.search_type}: {self.search_string}"
