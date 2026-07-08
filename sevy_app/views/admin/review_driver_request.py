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
        
        if approved:
            driver.is_approved = True
            driver.is_cancelled = False
            driver.save()
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
