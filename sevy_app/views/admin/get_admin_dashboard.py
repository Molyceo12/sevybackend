from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sevy_app.models import CustomUser, Company, Driver, SystemConfig, Transaction
from django.db.models import Sum

def get_stats_for_period(start_date=None):
    if start_date:
        company_count = Company.objects.filter(created_at__gte=start_date).count()
        if company_count == 0:
            company_count = CustomUser.objects.filter(user_type='company', date_joined__gte=start_date).count()
            
        customer_count = CustomUser.objects.filter(user_type='customer', date_joined__gte=start_date).count()
        
        driver_count = Driver.objects.filter(created_at__gte=start_date).count()
        if driver_count == 0:
            driver_count = CustomUser.objects.filter(user_type='driver', date_joined__gte=start_date).count()
            
        revenue_aggr = Transaction.objects.filter(created_at__gte=start_date, status='completed').aggregate(Sum('amount'))
        total_revenue = float(revenue_aggr['amount__sum'] or 0.0)
    else:
        company_count = Company.objects.count()
        if company_count == 0:
            company_count = CustomUser.objects.filter(user_type='company').count()
            
        customer_count = CustomUser.objects.filter(user_type='customer').count()
        
        driver_count = Driver.objects.count()
        if driver_count == 0:
            driver_count = CustomUser.objects.filter(user_type='driver').count()
            
        config = SystemConfig.objects.first()
        total_revenue = float(config.total_revenue) if config and config.total_revenue else 0.0
        
        if total_revenue == 0.0:
            revenue_aggr = Transaction.objects.filter(status='completed').aggregate(Sum('amount'))
            total_revenue = float(revenue_aggr['amount__sum'] or 0.0)
            
    return {
        "total_companies": company_count,
        "total_customers": customer_count,
        "total_drivers": driver_count,
        "total_revenue": total_revenue
    }

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def get_admin_dashboard(request):
    try:
        now_dt = timezone.now()
        
        daily_start = now_dt - timedelta(days=1)
        weekly_start = now_dt - timedelta(days=7)
        yearly_start = now_dt - timedelta(days=365)
        
        return Response({
            "code": 200,
            "status": True,
            "message": "Admin dashboard summary retrieved successfully",
            "body": {
                "all_time": get_stats_for_period(None),
                "yearly": get_stats_for_period(yearly_start),
                "weekly": get_stats_for_period(weekly_start),
                "daily": get_stats_for_period(daily_start)
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
