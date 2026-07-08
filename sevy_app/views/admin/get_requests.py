from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Driver, Company, Transaction

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_requests(request):
    try:
        # Fetch unapproved drivers
        unapproved_drivers = Driver.objects.select_related('userid').filter(is_approved=False)
        # Fetch unverified companies (and filter out soft-deleted ones)
        unverified_companies = Company.objects.filter(is_verified=False, is_deleted=False)
        # Fetch transactions waiting for approval
        waiting_transactions = Transaction.objects.select_related('user').filter(status__in=['waitingapproval', 'wait_approval', 'pending'])
        
        requests_list = []
        
        # Format driver requests
        for d in unapproved_drivers:
            requests_list.append({
                "request_type": "driver",
                "id": d.userid.custom_id,
                "name": d.full_name,
                "email": d.userid.email,
                "phone": d.phone_number,
                "vehicle": d.vehicle_make_color,
                "plate": d.plate_number,
                "created_at": d.created_at.isoformat() if d.created_at else None
            })
            
        # Format company requests
        for c in unverified_companies:
            requests_list.append({
                "request_type": "company",
                "id": c.company_id_id,
                "name": c.company_name or c.host_name,
                "email": c.contact_email,
                "phone": c.phone_number,
                "location": c.location,
                "rdb_certificate_url": c.rdb_certificate_url,
                "owner_id_url": c.owner_id_url,
                "created_at": c.created_at.isoformat() if c.created_at else None
            })
            
        # Format transaction requests
        for t in waiting_transactions:
            requests_list.append({
                "request_type": f"{t.transaction_type} request",
                "id": t.transaction_id,
                "name": t.user.email if t.user else "Unknown User",  # Safely handle if no user is attached
                "amount": float(t.amount) if t.amount else 0.00,
                "currency": t.currency,
                "created_at": t.created_at.isoformat() if t.created_at else None
            })
            
        # Sort the combined list by 'created_at' in descending order (newest top)
        requests_list.sort(key=lambda x: x["created_at"] if x["created_at"] else "", reverse=True)
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Pending requests retrieved successfully.",
            "total_requests": len(requests_list),
            "body": requests_list
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
