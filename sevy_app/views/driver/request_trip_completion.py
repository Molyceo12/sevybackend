from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Trip, Notification

@api_view(['POST'])
@permission_classes([AllowAny])
def request_trip_completion(request):
    try:
        trip_id = request.data.get('trip_id')
        
        if not trip_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required field (trip_id).",
                "body": {}
            }, status=400)
            
        trip = Trip.objects.filter(trip_id=trip_id).first()
        if not trip:
            return Response({
                "code": 404,
                "status": False,
                "message": "Trip not found.",
                "body": {}
            }, status=404)
            
        # Ensure it's not already completed
        if trip.status == 'completed' or trip.status == 'paid':
            return Response({
                "code": 400,
                "status": False,
                "message": f"This trip is already {trip.status}.",
                "body": {}
            }, status=400)
            
        # Send completion request notification to the customer
        Notification.objects.create(
            user=trip.userid,
            title="Driver Arrived / Trip Finished",
            message="Your driver has marked this trip as completed. Please confirm to finalize it.",
            notification_type='trip_completion',
            related_id=trip.trip_id
        )

        if trip.userid and trip.userid.email:
            from sevy_app.utils.email_service import send_notification_email
            send_notification_email(
                to_email=trip.userid.email,
                subject="Action Required: Confirm Trip Completion",
                message="Your driver has marked this trip as completed. Please log into the app and confirm or report this trip within the next 2 hours."
            )

        # Update the trip's approval_status to 'requestsent'
        trip.approval_status = 'requestsent'
        trip.save()
        
        # Schedule the Celery task to auto-accept the trip after 7 minutes (420 seconds) for testing
        from sevy_app.tasks import auto_accept_trip_completion_task
        auto_accept_trip_completion_task.apply_async(args=[trip.trip_id], countdown=420)
        
        return Response({
            "code": 200,
            "status": True,
            "message": "Completion request sent to customer.",
            "body": {
                "trip_id": trip.trip_id,
                "customer_notified": True
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
