from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Transaction, Company, CarBooking
from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny]) # Change this later to IsAdminUser if needed
def get_company_transactions(request):
    try:
        # Fetch transactions where user_type is 'company'
        transactions = Transaction.objects.filter(
            user__user_type='company'
        ).select_related('user', 'user__company_profile').order_by('-created_at')
        
        # Pre-fetch related car bookings for performance
        booking_ids = [t.related_id for t in transactions if t.transaction_type == 'carbooking' and t.related_id]
        bookings_map = {}
        if booking_ids:
            bookings = CarBooking.objects.filter(booking_id__in=booking_ids).select_related('car')
            for b in bookings:
                bookings_map[b.booking_id] = b
                
        transaction_list = []
        for t in transactions:
            
            # 1. Fetch Company Details
            company_data = []
            if t.user and hasattr(t.user, 'company_profile'):
                company = t.user.company_profile
                if company:
                    company_data.append({
                        "company_id": company.company_id_id,
                        "company_name": company.company_name,
                        "host_name": company.host_name,
                        "phone_number": company.phone_number,
                        "profile_image": company.profile_image if company.profile_image else None,
                        "total_bookings": company.total_bookings,
                        "total_income": float(company.total_income) if company.total_income else 0.0
                    })
                    
            # 2. Fetch Booking Details
            booking_data = []
            if t.transaction_type == 'carbooking' and t.related_id:
                booking = bookings_map.get(t.related_id)
                if booking:
                    booking_data.append({
                        "booking_id": booking.booking_id,
                        "booking_number": booking.booking_number,
                        "booking_type": booking.booking_type,
                        "status": booking.status,
                        "start_date": booking.start_date.isoformat() if booking.start_date else None,
                        "end_date": booking.end_date.isoformat() if booking.end_date else None,
                        "total_price": float(booking.total_price) if booking.total_price else 0.0,
                        "pickup_location": booking.pickup_location,
                        "dropoff_location": booking.dropoff_location,
                        "car_name": f"{booking.car.brand} {booking.car.name}" if booking.car else "Unknown",
                        "car_image": booking.car.images[0] if booking.car and booking.car.images else None
                    })
            
            transaction_list.append({
                "transaction_id": t.transaction_id,
                "transaction_type": t.transaction_type,
                "amount": float(t.amount) if t.amount else 0.00,
                "currency": t.currency,
                "status": t.status,
                "customer_approved": t.customer_approved,
                "company_email": t.user.email if t.user else "Unknown",
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "company": company_data,
                "booking": booking_data
            })
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Company transactions retrieved successfully.",
            "total_transactions": len(transaction_list),
            "body": transaction_list
        }, status=200)
        
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
