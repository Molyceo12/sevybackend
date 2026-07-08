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
            
            # Notify the driver that the customer denied it
            if trip.driverid and trip.driverid.userid:
                from sevy_app.models import Notification
                Notification.objects.create(
                    user=trip.driverid.userid,
                    title="Trip Completion Denied",
                    message=f"The customer has denied the completion request for trip {trip.tracking_number or trip.trip_id}. Support will review it.",
                    notification_type='trip_approval',
                    related_id=trip.trip_id
                )
            
            # Notify admins of the dispute
            notify_admins(
                title="Trip Dispute Reported",
                message=f"Customer reported an issue and denied completion for trip {trip.tracking_number or trip.trip_id}.",
                notification_type="system",
                related_id=trip.trip_id
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
            trip.status = 'completed'
            trip.approval_status = 'approved'
            trip.save()
            
            # Notify the driver that the customer confirmed it
            if trip.driverid and trip.driverid.userid:
                from sevy_app.models import Notification
                Notification.objects.create(
                    user=trip.driverid.userid,
                    title="Trip Confirmed",
                    message=f"The customer has confirmed the completion of the trip.",
                    notification_type='trip_approval',
                    related_id=trip.trip_id
                )
            
            # Notify admins of completion
            notify_admins(
                title="Trip Completed",
                message=f"Trip {trip.tracking_number or trip.trip_id} was successfully completed and approved.",
                notification_type="trip",
                related_id=trip.trip_id
            )
            
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
