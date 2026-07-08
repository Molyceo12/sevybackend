from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Company

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_company_requests(request):
    try:
        # Fetch unverified companies (registration requests)
        unverified_companies = Company.objects.filter(is_verified=False, is_deleted=False).order_by('-created_at')
        
        requests_list = []
        for c in unverified_companies:
            requests_list.append({
                "company_id": c.company_id_id,
                "name": c.company_name or c.host_name,
                "email": c.contact_email,
                "phone": c.phone_number,
                "location": c.location,
                "profile_image": c.profile_image,
                "rdb_certificate_url": c.rdb_certificate_url,
                "owner_id_url": c.owner_id_url,
                "created_at": c.created_at.isoformat() if c.created_at else None
            })
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Company registration requests retrieved successfully.",
            "total_requests": len(requests_list),
            "body": requests_list
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
