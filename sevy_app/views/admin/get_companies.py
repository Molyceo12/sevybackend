from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Company

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_companies(request):
    try:
        # Get sort_by parameter ('bookings' or 'income')
        sort_by = request.GET.get('sort_by', 'bookings')
        
        # Base queryset for active companies
        companies = Company.objects.filter(is_verified=True, is_deleted=False)
        total_count = companies.count()
        
        # Apply ordering based on parameter
        if sort_by == 'income':
            active_companies = companies.order_by('-total_income')
        else:
            active_companies = companies.order_by('-total_bookings')
            
        company_data = []
        for company in active_companies:
            company_data.append({
                "company_id": company.company_id_id,
                "host_name": company.host_name,
                "company_name": company.company_name,
                "profile_image": company.profile_image,
                "is_verified": company.is_verified,
                "phone_number": company.phone_number,
                "contact_email": company.contact_email,
                "location": company.location,
                "balance": float(company.balance) if company.balance else 0.00,
                "total_bookings": company.total_bookings,
                "total_income": float(company.total_income) if company.total_income else 0.00,
                "is_deleted": company.is_deleted,
                "created_at": company.created_at.isoformat() if company.created_at else None,
                "updated_at": company.updated_at.isoformat() if company.updated_at else None
            })
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Companies retrieved successfully.",
            "total_count": total_count,
            "body": company_data
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
