from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import SystemConfig, Transaction, PlatformCommission
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def admin_profile(request):
    try:
        config = SystemConfig.objects.first()
        
        # Lifetime Gross Income (Total volume of all completed transactions summed dynamically)
        lifetime_gross_aggr = Transaction.objects.filter(
            transaction_type='carbooking', 
            status='completed'
        ).aggregate(Sum('amount'))
        gross_income = float(lifetime_gross_aggr['amount__sum'] or 0.00)
        
        # Lifetime Total Revenue (Pulled explicitly from the SystemConfig specific table)
        total_revenue = float(config.total_revenue) if config and config.total_revenue else 0.00
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Monthly Gross Salary (Total volume of completed transactions in the last 30 days)
        monthly_gross_aggr = Transaction.objects.filter(
            transaction_type='carbooking', 
            status='completed',
            created_at__gte=thirty_days_ago
        ).aggregate(Sum('amount'))
        monthly_gross_salary = float(monthly_gross_aggr['amount__sum'] or 0.00)
        
        # Monthly Net Profit (Total platform commissions earned in the last 30 days)
        monthly_net_aggr = PlatformCommission.objects.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(Sum('commission_earned'))
        monthly_net_profit = float(monthly_net_aggr['commission_earned__sum'] or 0.00)
        
        # Fetch raw lists
        transactions = Transaction.objects.all().order_by('-created_at')[:200]
        commissions = PlatformCommission.objects.all().order_by('-created_at')[:200]
        
        transaction_list = []
        for t in transactions:
            transaction_list.append({
                "transaction_id": t.transaction_id,
                "type": t.transaction_type,
                "amount": float(t.amount) if t.amount else 0.00,
                "currency": t.currency,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None
            })
            
        commission_list = []
        for c in commissions:
            commission_list.append({
                "commission_id": c.commission_id,
                "transaction_id": c.transaction.transaction_id if c.transaction else None,
                "source_type": c.source_type,
                "total_amount": float(c.total_amount) if c.total_amount else 0.00,
                "commission_earned": float(c.commission_earned) if c.commission_earned else 0.00,
                "created_at": c.created_at.isoformat() if c.created_at else None
            })

        return Response({
            "code": 200,
            "status": True,
            "message": "Admin profile data retrieved successfully",
            "body": {
                "total_revenue": total_revenue,
                "monthly_gross_profit": monthly_gross_salary,
                "monthly_net_profit": monthly_net_profit,
                "transactions": transaction_list,
                "commissions": commission_list
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
