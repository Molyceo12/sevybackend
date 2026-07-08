from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Transaction

@api_view(['POST'])
@permission_classes([AllowAny])
def approve_completion(request):
    try:
        userid = request.data.get('userid')
        booking_id = request.data.get('booking_id')
        
        if not all([userid, booking_id]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (userid, booking_id).",
                "body": {}
            }, status=400)
            
        booking = CarBooking.objects.filter(booking_id=booking_id).first()
        if not booking:
            return Response({
                "code": 404,
                "status": False,
                "message": "Car booking not found.",
                "body": {}
            }, status=404)
            
        # Verify the user approving is the user who made the booking
        if booking.user.custom_id != userid:
            return Response({
                "code": 403,
                "status": False,
                "message": "Only the customer who made the booking can approve its completion.",
                "body": {}
            }, status=403)
            
        if booking.status == 'completed':
            return Response({
                "code": 400,
                "status": False,
                "message": "This booking is already marked as completed.",
                "body": {}
            }, status=400)

        # 1. Change booking status to completed
        booking.status = 'completed'
        booking.save()
        
        # 2. Find associated waitingapproval payout transactions and mark them as customer_approved
        transactions = Transaction.objects.filter(
            related_id=booking_id, 
            status='waitingapproval',
            customer_approved=False
        )
        
        approved_count = 0
        for transaction in transactions:
            transaction.customer_approved = True
            transaction.save()
            approved_count += 1
            
        return Response({
            "code": 200,
            "status": True,
            "message": "Booking marked as completed and payouts approved by customer.",
            "body": {
                "booking_id": booking.booking_id,
                "status": booking.status,
                "payouts_approved": approved_count
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
