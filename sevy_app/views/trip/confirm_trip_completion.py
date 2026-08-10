from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Notification, CustomUser
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_trip_completion(request):
    try:
        trip_id = request.data.get('trip_id')
        userid = request.data.get('userid')
        action = request.data.get('action', 'accept') # 'accept' or 'report'
        
        if not all([trip_id, userid]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (trip_id, userid).",
                "body": {}
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid).first()
        if not user:
            return Response({
                "code": 404,
                "status": False,
                "message": "User not found.",
                "body": {}
            }, status=404)
            
        trip = Trip.objects.filter(trip_id=trip_id, userid=user).first()
        if not trip:
            return Response({
                "code": 404,
                "status": False,
                "message": "Trip not found or does not belong to this user.",
                "body": {}
            }, status=404)
            
        if trip.status == 'completed' or trip.status == 'paid':
            return Response({
                "code": 400,
                "status": False,
                "message": "This trip is already finalized.",
                "body": {}
            }, status=400)
            
        if trip.approval_status != 'requestsent':
            return Response({
                "code": 400,
                "status": False,
                "message": f"Cannot modify. Trip approval status is already '{trip.approval_status}'.",
                "body": {}
            }, status=400)
            
        if action == 'report':
            trip.approval_status = 'denied'
            trip.save()
            
            # Notify Admins
            notify_admins(
                title="Trip Reported by Customer",
                message=f"Customer reported trip {trip.tracking_number or trip.trip_id}. It needs review.",
                notification_type="support",
                related_id=trip.trip_id
            )
            
            # Notify the driver that the customer denied it
            if trip.driverid and trip.driverid.userid:
                from sevy_app.models import Notification
                Notification.objects.create(
                    user=trip.driverid.userid,
                    title="Trip Completion Denied",
                    message=f"The customer has denied the completion request for trip {trip.tracking_number or trip.trip_id}. Support will review it.",
                    notification_type='drivertrip',
                    related_id=trip.trip_id
                )
                
                from sevy_app.utils.fcm_service import send_fcm_notification
                send_fcm_notification(
                    user=trip.driverid.userid,
                    title="Trip Completion Denied",
                    body=f"The customer has denied the completion request for trip {trip.tracking_number or trip.trip_id}. Support will review it.",
                    data={"type": "drivertrip", "trip_id": str(trip.trip_id)}
                )
                
                if trip.driverid.userid.email:
                    from sevy_app.utils.email_service import send_notification_email
                    driver_name = trip.driverid.userid.user_info.full_names if hasattr(trip.driverid.userid, 'user_info') else 'Driver'
                    send_notification_email(
                        to_email=trip.driverid.userid.email,
                        subject="Trip Completion Denied",
                        name=driver_name,
                        message=f"The customer has denied the completion request for trip {trip.tracking_number or trip.trip_id}. Support will review it."
                    )
            

            
            return Response({
                "code": 200,
                "status": True,
                "message": "Trip completion request has been reported to support.",
                "body": {
                    "trip_id": trip.trip_id,
                    "approval_status": trip.approval_status
                }
            }, status=200)

        else:
            # Default to Accept
            trip.approval_status = 'approved'
            trip.save()
            
            # Notify the driver that the customer confirmed it
            if trip.driverid and trip.driverid.userid:
                from sevy_app.models import Notification
                from sevy_app.utils.fcm_service import send_fcm_notification
                
                Notification.objects.create(
                    user=trip.driverid.userid,
                    title="Trip Confirmed",
                    message=f"The customer has confirmed the completion of the trip.",
                    notification_type='drivertrip',
                    related_id=trip.trip_id
                )
                
                send_fcm_notification(
                    user=trip.driverid.userid,
                    title="Trip Confirmed",
                    body="The customer has confirmed the completion of the trip.",
                    data={"type": "drivertrip", "trip_id": str(trip.trip_id)}
                )
                
                if trip.driverid.userid.email:
                    from sevy_app.utils.email_service import send_notification_email
                    driver_name = trip.driverid.userid.user_info.full_names if hasattr(trip.driverid.userid, 'user_info') else 'Driver'
                    send_notification_email(
                        to_email=trip.driverid.userid.email,
                        subject="Trip Confirmed",
                        name=driver_name,
                        message=f"The customer has confirmed the completion of trip {trip.tracking_number or trip.trip_id}."
                    )
            

            
            # Email Customer
            if trip.userid and trip.userid.email:
                from sevy_app.utils.email_service import send_notification_email
                customer_name = trip.userid.user_info.full_names if hasattr(trip.userid, 'user_info') else 'Customer'
                send_notification_email(
                    to_email=trip.userid.email,
                    subject="Trip Completed",
                    name=customer_name,
                    message=f"Thank you for riding with Sevy Mobility! Your trip {trip.tracking_number or trip.trip_id} has been marked as completed.",
                    action_text="View Receipt",
                    action_url="https://sevymobility.com/trips"
                )
                
            # Notify Admins
            tx_type = "company_transaction" if (trip.driverid and trip.driverid.companyid) else "driver_transaction"
            try:
                notify_admins(
                    title="Trip Completion Request",
                    message=f"A completion request for trip {trip.tracking_number or trip.trip_id} requires your review and approval.",
                    notification_type=tx_type,
                    related_id=trip.trip_id
                )
            except Exception as e:
                print(f"\\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                print(f"Trip Completion Notification Error:\\n{str(e)}")
                print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\\n")
            

            return Response({
                "code": 200,
                "status": True,
                "message": "Trip has been officially completed.",
                "body": {
                    "trip_id": trip.trip_id,
                    "status": trip.status,
                    "approval_status": trip.approval_status
                }
            }, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
