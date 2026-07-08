from django.db import models
from django.conf import settings

import secrets

def generate_custom_id():
    return secrets.token_hex(12)

# Alias for old migrations
def generate_category_id():
    return generate_custom_id()

class ExploreCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_custom_id, editable=False)
    categoryname = models.CharField(max_length=100)

    class Meta:
        db_table = 'explorecategory'

    def __str__(self):
        return self.categoryname

class Explore(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=generate_custom_id, editable=False)
    companyid = models.CharField(max_length=50) # Just a key, not a ForeignKey
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ExploreCategory, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.CharField(max_length=100)
    features = models.JSONField(default=list) # Array field
    images = models.JSONField(default=list) # Array of image paths/URLs
    place = models.CharField(max_length=255)

    class Meta:
        db_table = 'explore'

    def __str__(self):
        return f"{self.name} ({self.subcategory})"
