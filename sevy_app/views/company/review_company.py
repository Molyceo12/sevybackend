from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from sevy_app.models import Company
from sevy_app.models.user import CustomUser

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_company(request):
    """
    Review a company registration request.
    Payload can contain {"approved": true} or {"cancelled": true, "reason": "..."}
    """
    if request.user.user_type != 'admin':
        return Response({"status": False, "message": "Unauthorized access."}, status=status.HTTP_403_FORBIDDEN)

    company_id = request.data.get('company_id')
    approved = request.data.get('approved', False)
    cancelled = request.data.get('cancelled', False)
    reason = request.data.get('reason', '')

    if not company_id:
        return Response({"status": False, "message": "company_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        company = Company.objects.get(company_id=company_id)
        
        if approved:
            company.is_verified = True
            company.is_cancelled = False
            company.save()
            return Response({
                "status": True, 
                "message": "Company approved successfully.", 
                "body": {"company_id": company.company_id_id, "is_verified": True}
            })
            
        elif cancelled:
            company.is_verified = False
            company.is_cancelled = True
            company.cancellation_reason = reason
            company.save()
            return Response({
                "status": True, 
                "message": "Company cancelled successfully.", 
                "body": {"company_id": company.company_id_id, "is_cancelled": True}
            })
            
        else:
            return Response({"status": False, "message": "Must provide approved: true or cancelled: true."}, status=status.HTTP_400_BAD_REQUEST)

    except Company.DoesNotExist:
        return Response({"status": False, "message": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
