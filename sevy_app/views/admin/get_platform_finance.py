from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import SystemConfig, Transaction

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_platform_finance(request):
    try:
        # Fetch the system config
        config = SystemConfig.objects.first()
        
        total_revenue = float(config.total_revenue) if config else 0.00
        gross_income = float(config.gross_income) if config else 0.00
        net_income = total_revenue  # For the platform, revenue from commissions = net income
        
        # Fetch transactions
        # Pending ones usually have status 'waitingapproval' or 'pending'
        pending_trx_qs = Transaction.objects.select_related('user').filter(status__in=['waitingapproval', 'pending', 'wait_approval']).order_by('-created_at')
        
        # Completed ones usually have status 'approved', 'completed', 'paid'
        completed_trx_qs = Transaction.objects.select_related('user').filter(status__in=['approved', 'completed', 'paid']).order_by('-created_at')
        
        pending_count = pending_trx_qs.count()
        completed_count = completed_trx_qs.count()

        # Helper to serialize a transaction safely
        def serialize_trx(trx):
            return {
                "transaction_id": trx.transaction_id,
                "amount": float(trx.amount),
                "currency": trx.currency,
                "status": trx.status,
                "transaction_type": trx.transaction_type,
                "payment_method": trx.payment_method,
                "description": trx.description,
                "created_at": trx.created_at.isoformat() if trx.created_at else None,
                "user": trx.user.email if trx.user else None,
            }

        # Limit to 100 items so the payload isn't massive and parsing is fast
        pending_trx = [serialize_trx(trx) for trx in pending_trx_qs[:100]]
        completed_trx = [serialize_trx(trx) for trx in completed_trx_qs[:100]]

        return Response({
            "code": 200,
            "status": True,
            "message": "Platform financial data retrieved successfully.",
            "body": {
                "total_revenue": total_revenue,
                "gross_income": gross_income,
                "net_income": net_income,
                "pending_transactions": pending_trx,
                "completed_transactions": completed_trx,
                "pending_count": pending_count,
                "completed_count": completed_count
            }
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
