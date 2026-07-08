from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models.driver import Driver
from sevy_app.utils.notifications import notify_admins

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_driver_documents(request, driver_id):
    try:
        driver = Driver.objects.get(userid=driver_id)
    except Driver.DoesNotExist:
        return Response({"error": "Driver not found."}, status=status.HTTP_404_NOT_FOUND)

    # As requested, this accepts default URLs (strings) or actual files for now.
    # We will refine this later.
    driving_license = request.FILES.get('driving_license') or request.data.get('driving_license')
    government_id = request.FILES.get('government_id') or request.data.get('government_id')
    
    updated = False
    if driving_license:
        driver.driving_license = driving_license
        updated = True
    if government_id:
        driver.government_id = government_id
        updated = True
        
    if updated:
        # Reset cancellation status since they provided new documents
        driver.is_cancelled = False
        driver.cancellation_reason = ""
        driver.is_approved = False # Wait for admin to approve the new documents
        driver.save()
        
        notify_admins(
            title="Documents Updated",
            message=f"Driver {driver.userid.user_info.full_names if hasattr(driver.userid, 'user_info') else driver.userid.custom_id} updated their documents.",
            notification_type="system",
            related_id=driver.userid.custom_id
        )
        
        return Response({
            "message": "Documents updated successfully. Awaiting admin review."
        }, status=status.HTTP_200_OK)
        
    return Response({
        "error": "No documents provided to update."
    }, status=status.HTTP_400_BAD_REQUEST)
