from sevy_app.models import CustomUser, Notification
from sevy_app.utils.fcm_service import send_fcm_notification

def notify_admins(title, message, notification_type='system', related_id=None):
    """
    Creates a single notification assigned to the first available admin.
    Because admins share notifications, this effectively notifies all admins.
    Also sends FCM push notifications to all admin devices.
    """
    if not notification_type.startswith('admin'):
        notification_type = f"admin{notification_type}"
        
    admins = CustomUser.objects.filter(user_type='admin')
    
    # Send push notifications and emails to all admin users
    from sevy_app.utils.email_service import send_admin_email_notification
    for admin_user in admins:
        # Push notification
        send_fcm_notification(
            user=admin_user,
            title=title,
            body=message,
            data={"type": notification_type, "id": str(related_id) if related_id else ""}
        )
        
        # Email notification
        if admin_user.email:
            send_admin_email_notification(
                to_email=admin_user.email,
                subject=title,
                message=message,
                notification_type=notification_type,
                details={"Item ID": str(related_id)} if related_id else None
            )

    # Create the database notification for the first admin (shared inbox)
    admin = admins.first()
    if admin:
        Notification.objects.create(
            user=admin,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id
        )
