from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from sevy_app.models import Driver

@api_view(['POST'])
@permission_classes([AllowAny]) # Keep AllowAny for now, or IsAdminUser if needed
def review_driver_request(request):
    """
    Approves or rejects a driver request.
    Payload can contain {"approved": true} or {"cancelled": true, "reason": "..."}
    Requires "driver_id" (user custom id)
    """
    try:
        driver_id = request.data.get('driver_id')
        approved = request.data.get('approved', False)
        cancelled = request.data.get('cancelled', False)
        reason = request.data.get('reason', '')
        
        if not driver_id:
            return Response({"status": False, "message": "driver_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        driver = Driver.objects.get(userid__custom_id=driver_id)
        
        from sevy_app.utils.email_service import send_notification_email

        if approved:
            driver.is_approved = True
            driver.is_cancelled = False
            driver.save()
            
            send_notification_email(
                to_email=driver.userid.email,
                subject="Your Account is Approved!",
                name=driver.userid.user_info.full_names if hasattr(driver.userid, 'user_info') else 'Driver',
                message="Great news! Your account has been reviewed and approved. You can now log into the Sevy app and start accepting trips.",
                action_text="Open App",
                action_url="https://sevymobility.com"
            )
            
            from sevy_app.models import Notification
            from sevy_app.utils.fcm_service import send_fcm_notification
            
            title = "Account Approved"
            msg = "Great news! Your account has been reviewed and approved. You can now start accepting trips."
            Notification.objects.create(
                user=driver.userid,
                title=title,
                message=msg,
                notification_type='driversystem',
                related_id=driver_id
            )
            send_fcm_notification(
                user=driver.userid,
                title=title,
                body=msg,
                data={"type": "driversystem", "driver_id": driver_id}
            )
            
            return Response({
                "code": 200,
                "status": True,
                "message": "Driver approved successfully.", 
            }, status=200)
            
        elif cancelled:
            driver.is_approved = False
            driver.is_cancelled = True
            driver.cancellation_reason = reason
            driver.save()
            
            send_notification_email(
                to_email=driver.userid.email,
                subject="Update on your Sevy Mobility Application",
                name=driver.userid.user_info.full_names if hasattr(driver.userid, 'user_info') else 'Driver',
                message=f"We have reviewed your application. Unfortunately, we cannot approve your account at this time.<br><br>Reason: {reason}",
                action_text="Contact Support",
                action_url="mailto:support@sevymobility.com"
            )
            
            from sevy_app.models import Notification
            from sevy_app.utils.fcm_service import send_fcm_notification
            
            title = "Account Application Update"
            msg = f"Your application was reviewed and could not be approved at this time. Reason: {reason}"
            Notification.objects.create(
                user=driver.userid,
                title=title,
                message=msg,
                notification_type='driversystem',
                related_id=driver_id
            )
            send_fcm_notification(
                user=driver.userid,
                title=title,
                body=msg,
                data={"type": "driversystem", "driver_id": driver_id}
            )
            
            return Response({
                "code": 200,
                "status": True,
                "message": "Driver request rejected.",
            }, status=200)
            
        else:
            return Response({"status": False, "message": "Must provide approved: true or cancelled: true."}, status=status.HTTP_400_BAD_REQUEST)
            
    except Driver.DoesNotExist:
        return Response({
            "status": False, 
            "message": f"Driver with ID {driver_id} not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
