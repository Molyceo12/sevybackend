import secrets
from django.db import models
from .car import Car
from .user import CustomUser

def generate_review_id():
    return secrets.token_hex(12)

class CarReview(models.Model):
    review_id = models.CharField(max_length=50, primary_key=True, default=generate_review_id)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='car_reviews')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, help_text="Rating from 1.0 to 5.0")
    review_text = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'car_reviews'
        unique_together = ('user', 'car') # Enforce 1 review per user per car
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.custom_id} for {self.car.car_id} ({self.rating})"
