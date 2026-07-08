from sevy_app.models import CustomUser, Notification

def notify_admins(title, message, notification_type='system', related_id=None):
    """
    Creates a single notification assigned to the first available admin.
    Because admins share notifications, this effectively notifies all admins.
    """
    admin = CustomUser.objects.filter(user_type='admin').first()
    if admin:
        Notification.objects.create(
            user=admin,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
