import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy_backend.settings')
django.setup()

from sevy_app.models import Notification, CarBooking

notifs = Notification.objects.filter(notification_type='rental')
print(f"Total rental notifications: {notifs.count()}")

for n in notifs[:5]:
    print(f"ID: {n.notification_id}, User: {n.user.email}, Related ID: {n.related_id}")
    booking = CarBooking.objects.filter(booking_id=n.related_id).select_related('car').first()
    if booking and booking.car and booking.car.images:
        print(f"  Image: {booking.car.images[0]}")
    else:
        print(f"  No image found for related_id={n.related_id}")
