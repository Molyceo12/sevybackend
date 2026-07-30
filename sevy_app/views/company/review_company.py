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
            company.save()
            
            if company.company_id and company.company_id.email:
                from sevy_app.utils.email_service import send_notification_email
                send_notification_email(
                    to_email=company.company_id.email,
                    subject="Your Company Account is Approved!",
                    message="Great news! Your company registration has been reviewed and approved. You can now manage your fleet.",
                    action_text="Log In",
                    action_url="https://sevymobility.com"
                )
                
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
            company.save()
            
            if company.company_id and company.company_id.email:
                from sevy_app.utils.email_service import send_notification_email
                send_notification_email(
                    to_email=company.company_id.email,
                    subject="Update on your Company Registration",
                    message=f"We have reviewed your registration. Unfortunately, it was rejected.<br><br>Reason: {reason}",
                    action_text="Contact Support",
                    action_url="mailto:support@sevymobility.com"
                )
                
            return Response({
                "status": True, 
                "message": "Company cancelled successfully.", 
                "body": {"company_id": company.company_id_id, "is_cancelled": True}
            })
            
        else:
            return Response({"status": False, "message": "Must provide approved: true or cancelled: true."}, status=status.HTTP_400_BAD_REQUEST)

    except Company.DoesNotExist:
        return Response({"status": False, "message": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
