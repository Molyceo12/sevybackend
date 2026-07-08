from django.db import models
from .car import Car
from .user import CustomUser

class CarLike(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='liked_cars')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'car_likes'
        unique_together = ('user', 'car')
        ordering = ['-created_at']

    def __str__(self):
        return f"User {self.user_id} likes Car {self.car_id}"
