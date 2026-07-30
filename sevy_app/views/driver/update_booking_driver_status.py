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
            from sevy_app.utils.fcm_service import send_fcm_notification
            from sevy_app.utils.email_service import send_notification_email
            
            Notification.objects.create(
                user=booking.user,
                title="Driver Accepted",
                message=f"Your driver {driver.full_name} has accepted your rental request.",
                notification_type='rental',
                related_id=booking.booking_id
            )
            car_image = booking.car.images[0] if booking.car and booking.car.images else None
            send_fcm_notification(
                user=booking.user,
                title="Driver Accepted",
                body=f"Your driver {driver.full_name} has accepted your rental request.",
                data={"type": "rental", "booking_id": str(booking.booking_id)},
                image=car_image
            )
            if booking.user and hasattr(booking.user, 'email'):
                customer_name = booking.user.user_info.full_names if hasattr(booking.user, 'user_info') else 'Customer'
                send_notification_email(
                    to_email=booking.user.email,
                    subject="Driver Accepted",
                    name=customer_name,
                    message=f"Your driver {driver.full_name} has accepted your rental request."
                )
            
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                start_date_str = booking.start_date.strftime('%b %d, %Y %H:%M') if booking.start_date else ''
                end_date_str = booking.end_date.strftime('%b %d, %Y %H:%M') if booking.end_date else ''
                
                Notification.objects.create(
                    user=company_user,
                    title="Driver accepted booking",
                    message=f"Driver {driver.full_name} has accepted the booking for your {booking.car.brand} {booking.car.name} from {start_date_str} to {end_date_str}.",
                    notification_type="companybooking",
                    related_id=booking.booking_id
                )
                car_image = booking.car.images[0] if booking.car and booking.car.images else None
                send_fcm_notification(
                    user=company_user,
                    title="Driver accepted booking",
                    body=f"Driver {driver.full_name} has accepted the booking for your {booking.car.brand} {booking.car.name} from {start_date_str} to {end_date_str}.",
                    data={"type": "companybooking", "booking_id": str(booking.booking_id)},
                    image=car_image
                )
                if hasattr(company_user, 'email'):
                    company_name = company_user.user_info.full_names if hasattr(company_user, 'user_info') else 'Partner'
                    send_notification_email(
                        to_email=company_user.email,
                        subject="Driver accepted booking",
                        name=company_name,
                        message=f"Driver {driver.full_name} has accepted the booking for your {booking.car.brand} {booking.car.name} from {start_date_str} to {end_date_str}."
                    )
        elif driver_status == 'rejected':
            driver.is_available = True
            driver.save()
            
            # Remove driver and reset to pending
            booking.driver = None
            booking.status = 'pending'
            
            from sevy_app.models import Notification
            from sevy_app.utils.fcm_service import send_fcm_notification
            from sevy_app.utils.email_service import send_notification_email
            from sevy_app.utils.notifications import notify_admins
            
            # Notify Admins
            notify_admins(
                title="Booking Rejected by Driver",
                message=f"Driver {driver.full_name} rejected booking {booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id}.",
                notification_type="booking_cancelled",
                related_id=booking.booking_id
            )
            
            Notification.objects.create(
                user=booking.user,
                title="Booking Request Rejected",
                message=f"Your driver {driver.full_name} has rejected your rental request.",
                notification_type='rental',
                related_id=booking.booking_id
            )
            car_image = booking.car.images[0] if booking.car and booking.car.images else None
            send_fcm_notification(
                user=booking.user,
                title="Booking Request Rejected",
                body=f"Your driver {driver.full_name} has rejected your rental request.",
                data={"type": "rental", "booking_id": str(booking.booking_id)},
                image=car_image
            )
            if booking.user and hasattr(booking.user, 'email'):
                customer_name = booking.user.user_info.full_names if hasattr(booking.user, 'user_info') else 'Customer'
                send_notification_email(
                    to_email=booking.user.email,
                    subject="Booking Request Rejected",
                    name=customer_name,
                    message=f"Your driver {driver.full_name} has rejected your rental request."
                )
            
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Driver Rejected Booking",
                    message=f"Driver {driver.full_name} has rejected the assignment for your {booking.car.brand} {booking.car.name}.",
                    notification_type="companybooking",
                    related_id=booking.booking_id
                )
                car_image = booking.car.images[0] if booking.car and booking.car.images else None
                send_fcm_notification(
                    user=company_user,
                    title="Driver Rejected Booking",
                    body=f"Driver {driver.full_name} has rejected the assignment for your {booking.car.brand} {booking.car.name}.",
                    data={"type": "companybooking", "booking_id": str(booking.booking_id)},
                    image=car_image
                )
                if hasattr(company_user, 'email'):
                    company_name = company_user.user_info.full_names if hasattr(company_user, 'user_info') else 'Partner'
                    send_notification_email(
                        to_email=company_user.email,
                        subject="Driver Rejected Booking",
                        name=company_name,
                        message=f"Driver {driver.full_name} has rejected the assignment for your {booking.car.brand} {booking.car.name}."
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
