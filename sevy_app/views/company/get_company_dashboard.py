from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum
from sevy_app.models import Company, Notification, CarBooking, Car, Driver

@api_view(['POST'])
@permission_classes([AllowAny])
def get_company_dashboard(request):
    """
    Returns a comprehensive dashboard for a given company.
    Includes details, notifications, vehicles, active bookings, drivers, and total earnings.
    Expects company_id in the request body.
    """
    company_id = request.data.get('company_id')
    if not company_id:
        return Response({
            "status": "error",
            "message": "company_id is required in the request body",
            "body": {}
        }, status=400)

    try:
        company = Company.objects.select_related('company_id').get(company_id=company_id)
        
        if company.is_deleted:
            return Response({
                "status": "error",
                "message": "This company account has been deleted.",
                "body": {}
            }, status=404)
        
        # 1. Notifications linked to the company's user account
        notifications = Notification.objects.filter(user=company.company_id).order_by('-created_at')
        # 1. Notifications linked to the company's user account
        notifications_count = Notification.objects.filter(user=company.company_id).count()

        # 2. Vehicles (Cars) linked to the company
        cars_count = Car.objects.filter(companyid=company, is_deleted=False).count()

        # 3. Drivers linked to the company
        drivers_count = Driver.objects.filter(companyid=company).count()

        # 4. Bookings linked to the company
        active_status = ['ongoing', 'confirmed', 'pending']
        active_bookings_count = CarBooking.objects.filter(companyid=company, status__in=active_status).count()
        total_bookings_count = CarBooking.objects.filter(companyid=company).count()

        # 5. Total Earnings (Sum of total_price where payment_status='paid')
        earnings_result = CarBooking.objects.filter(companyid=company, payment_status='paid').aggregate(total_earnings=Sum('total_price'))
        total_earnings = earnings_result['total_earnings'] if earnings_result['total_earnings'] else 0.0

        # 6. Transactions (Linked via company's bookings)
        transactions_count = CarBooking.objects.filter(companyid=company, transaction__isnull=False).count()

        # Construct final response
        response_data = {
            "company_info": {
                "id": company.company_id_id,
                "name": company.company_name or company.host_name,
                "host_name": company.host_name,
                "email": company.contact_email,
                "phone_number": company.phone_number,
                "is_verified": company.is_verified,
                "is_cancelled": company.is_cancelled,
                "cancellation_reason": company.cancellation_reason,
                "location": company.location,
                "balance": float(company.balance),
                "bonuses": float(company.bonuses)
            },
            "notifications": {
                "total": notifications_count
            },
            "vehicles": {
                "total": cars_count
            },
            "drivers": {
                "total": drivers_count
            },
            "active_bookings": {
                "total": active_bookings_count
            },
            "bookings": {
                "total": total_bookings_count
            },
            "transactions": {
                "total": transactions_count
            },
            "total_earnings": total_earnings
        }

        return Response({
            "status": "success",
            "message": "Company dashboard retrieved successfully",
            "body": response_data
        }, status=200)

    except Company.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Company not found",
            "body": {}
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "body": {}
        }, status=500)
