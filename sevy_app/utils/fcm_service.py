from firebase_admin import messaging

def send_fcm_notification(user, title, body, data=None):
    """
    Sends an FCM push notification to all active devices of a given CustomUser.
    
    :param user: The CustomUser instance to notify.
    :param title: The title of the notification.
    :param body: The body message of the notification.
    :param data: Optional dictionary of data payload.
    :return: True if at least one message was sent, False otherwise.
    """
    fcm_devices = user.fcm_devices.filter(is_loggedin=True)
    if not fcm_devices.exists():
        print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(f"1.devicefounds : 0")
        print(f"2.notifications send successfully : 0")
        print(f"3.Failed to send : 0")
        print(f"4.Reason : No active devices found for user {user.email}")
        print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        return False
        
    try:
        tokens = [device.fcm_token for device in fcm_devices]
        
        # Prepare the message payload
        notification = messaging.Notification(
            title=title,
            body=body,
        )
        
        message = messaging.MulticastMessage(
            notification=notification,
            data=data if data else {},
            tokens=tokens,
        )
        
        # Send the message
        response = messaging.send_each_for_multicast(message)
        
        print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(f"1.devicefounds : {fcm_devices.count()}")
        print(f"2.notifications send successfully : {response.success_count}")
        print(f"3.Failed to send : {response.failure_count}")
        if response.failure_count > 0:
            print(f"4.Target User : {user.email} (Some devices failed)")
        else:
            print(f"4.Target User : {user.email}")
        print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        
        return response.success_count > 0
        
    except Exception as e:
        print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(f"1.devicefounds : {fcm_devices.count()}")
        print(f"2.notifications send successfully : 0")
        print(f"3.Failed to send : {fcm_devices.count()}")
        print(f"4.Error : {str(e)}")
        print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        return False
