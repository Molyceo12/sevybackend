from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models.company import Company
from sevy_app.utils.notifications import notify_admins

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_company_documents(request, company_id):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

    rdb_certificate_url = request.FILES.get('rdb_certificate_url') or request.data.get('rdb_certificate_url')
    owner_id_url = request.FILES.get('owner_id_url') or request.data.get('owner_id_url')
    
    updated = False
    if rdb_certificate_url:
        company.rdb_certificate_url = rdb_certificate_url
        updated = True
    if owner_id_url:
        company.owner_id_url = owner_id_url
        updated = True
        
    if updated:
        # Reset cancellation status since they provided new documents
        company.is_cancelled = False
        company.cancellation_reason = ""
        company.is_verified = False # Wait for admin to approve the new documents
        company.save()
        
        notify_admins(
            title="Company Documents Updated",
            message=f"Company {company.host_name} updated their documents.",
            notification_type="system",
            related_id=company.company_id.custom_id if hasattr(company.company_id, 'custom_id') else str(company.company_id)
        )
        
        return Response({
            "message": "Documents updated successfully. Awaiting admin review."
        }, status=status.HTTP_200_OK)
        
    return Response({
        "error": "No documents provided to update."
    }, status=status.HTTP_400_BAD_REQUEST)
