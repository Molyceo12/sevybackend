from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Company, Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def get_company_transactions(request):
    try:
        company_id = request.data.get('company_id')
        if not company_id:
            return Response({
                "code": 400,
                "status": False,
                "message": "company_id is required in the request body.",
                "body": []
            }, status=400)
            
        # Verify company exists
        company = Company.objects.filter(company_id=company_id).first()
        if not company:
            return Response({
                "code": 404,
                "status": False,
                "message": "Company not found.",
                "body": []
            }, status=404)

        # Fetch all transactions linked directly to this company's user account
        # And any withdrawals linked to the company
        from django.db.models import Q
        from sevy_app.models import CarBooking
        
        transactions = Transaction.objects.filter(
            Q(user=company.company_id) | Q(related_id=company_id)
        ).order_by('-created_at')

        results = []
        for tx in transactions:
            title = None
            subtitle = None
            image_url = None
            
            if tx.transaction_type == 'carbooking' and tx.related_id:
                booking = CarBooking.objects.filter(booking_id=tx.related_id).first()
                if booking:
                    if booking.user and hasattr(booking.user, 'user_info'):
                        title = booking.user.user_info.full_names
                    elif booking.user:
                        title = "Customer"
                        
                    if booking.car:
                        subtitle = booking.car.name
                        if booking.car.images and len(booking.car.images) > 0:
                            image_url = booking.car.images[0]
            elif tx.transaction_type == 'withdrawal':
                title = "Withdrawal"
                subtitle = tx.payment_method or "Mobile Money"

            body = {
                "transaction_id": tx.transaction_id,
                "reference_number": tx.reference_number,
                "transaction_type": tx.transaction_type,
                "related_id": tx.related_id,
                "amount": float(tx.amount) if tx.amount else 0.0,
                "currency": tx.currency,
                "payment_method": tx.payment_method,
                "status": tx.status,
                "description": tx.description,
                "created_at": tx.created_at,
                "completed_at": tx.completed_at,
                "metadata": {
                    "title": title,
                    "subtitle": subtitle,
                    "image_url": image_url
                }
            }
            results.append(body)

        return Response({
            "code": 200,
            "status": True,
            "message": "Company transactions fetched successfully.",
            "body": results
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": []
        }, status=500)
