from firebase_admin import messaging

def send_fcm_notification(user, title, body, data=None, image=None):
    """
    Hands off the push notification to a Celery background task so it doesn't block the API response.
    """
    from sevy_app.tasks import send_fcm_notification_task
    try:
        if user and user.id:
            send_fcm_notification_task.delay(user.id, title, body, data, image)
            return True
    except Exception as e:
        print(f"Failed to queue FCM task: {str(e)}")
    return False

def _execute_send_fcm_notification(user, title, body, data=None, image=None):
    """
    Actually executes the FCM push notification (runs in Celery background worker).
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
        # Firebase requires an absolute URL for images.
        if image and isinstance(image, str):
            if image.startswith('/') or not image.startswith('http'):
                # If the image is local (relative), the phone will get a 404 when downloading from sevymobility.com 
                # because it only exists on your laptop. Android drops notifications if the image download fails!
                # We will use a public placeholder car image so you can test it on your phone.
                image = "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=800&q=80"
                
        tokens = [device.fcm_token for device in fcm_devices]
        
        # Prepare the message payload
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image
        )
        
        # Configure for Android: High priority wakes up the device from Doze mode
        android_config = messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                sound='default'
            )
        )
        
        # Configure for iOS: APNS payload
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    content_available=True,
                )
            )
        )
        
        message = messaging.MulticastMessage(
            notification=notification,
            data=data if data else {},
            tokens=tokens,
            android=android_config,
            apns=apns_config
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
