from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Driver

@api_view(['POST'])
@permission_classes([AllowAny])
def update_booking_driver_status(request):
    try:
        booking_id = request.data.get('booking_id')
        driver_status = request.data.get('driver_status')
        
        if not booking_id or not driver_status:
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields (booking_id, driver_status).",
                "body": {}
            }, status=400)
            
        booking = CarBooking.objects.filter(booking_id=booking_id).first()
        if not booking:
            return Response({
                "code": 404,
                "status": False,
                "message": "Booking not found.",
                "body": {}
            }, status=404)
            
        driver = booking.driver
        if not driver:
            return Response({
                "code": 400,
                "status": False,
                "message": "This booking does not have an assigned driver.",
                "body": {}
            }, status=400)
            
        booking.driver_status = driver_status
        
        if driver_status == 'accepted':
            driver.is_available = False
            driver.save()
            
            from sevy_app.models import Notification
            Notification.objects.create(
                user=booking.user,
                title="Driver Accepted",
                message=f"Your driver {driver.full_name} has accepted your rental request.",
                notification_type='rental',
                related_id=booking.booking_id
            )
            
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Driver Accepted Assignment",
                    message=f"Driver {driver.full_name} has accepted the assignment for your {booking.car.brand} {booking.car.name}.",
                    notification_type="rental",
                    related_id=booking.booking_id
                )
            
        elif driver_status == 'rejected':
            driver.is_available = True
            driver.save()
            
            # Remove driver and reset to pending
            booking.driver = None
            booking.status = 'pending'
            
            from sevy_app.models import Notification
            Notification.objects.create(
                user=booking.user,
                title="Booking Request Rejected",
                message=f"Your driver {driver.full_name} has rejected your rental request.",
                notification_type='rental',
                related_id=booking.booking_id
            )
            
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Driver Rejected Booking",
                    message=f"Driver {driver.full_name} has rejected the assignment for your {booking.car.brand} {booking.car.name}.",
                    notification_type="rental",
                    related_id=booking.booking_id
                )

        booking.save()
        
        return Response({
            "code": 200,
            "status": True,
            "message": f"Booking driver status updated to {driver_status}.",
            "body": {
                "booking_id": booking.booking_id,
                "driver_status": booking.driver_status
            }
        }, status=200)

    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
