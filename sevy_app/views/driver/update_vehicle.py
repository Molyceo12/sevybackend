from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models.driver import Driver

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_driver_vehicle(request, driver_id):
    try:
        driver = Driver.objects.get(userid=driver_id)
    except Driver.DoesNotExist:
        return Response({"error": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)

    vehicle_make_color = request.data.get('vehicle_make_color')
    plate_number = request.data.get('plate_number')
    
    updated = False
    if vehicle_make_color:
        driver.vehicle_make_color = vehicle_make_color
        updated = True
    if plate_number:
        driver.plate_number = plate_number
        updated = True
        
    if updated:
        driver.is_cancelled = False
        driver.cancellation_reason = ""
        driver.is_approved = False
        driver.save()
        
        return Response({
            "message": "Vehicle details updated successfully. Awaiting admin review."
        }, status=status.HTTP_200_OK)
        
    return Response({
        "error": "No vehicle details provided to update."
    }, status=status.HTTP_400_BAD_REQUEST)
