from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, Notification, Transaction, CustomUser
from sevy_app.utils.notifications import notify_admins

@api_view(['POST'])
@permission_classes([AllowAny])
def update_booking_status(request):
    """
    Updates the status of a booking.
    Expects JSON body: {"booking_id": "id", "ongoing": true} 
    (or confirmed: true, completed: true, cancelled: true)
    """
    booking_id = request.data.get('booking_id')

    if not booking_id:
        return Response({
            "status": "error",
            "message": "booking_id is required in the request body",
            "body": {}
        }, status=400)
        
    new_status = None
    
    # Check boolean flags in the request
    if request.data.get('ongoing') in [True, 'true', 'True']:
        new_status = 'ongoing'
    elif request.data.get('confirmed') in [True, 'true', 'True']:
        new_status = 'confirmed'
    elif request.data.get('completed') in [True, 'true', 'True']:
        new_status = 'completed'
    elif request.data.get('cancelled') in [True, 'true', 'True'] or request.data.get('ongoing') in [False, 'false', 'False'] or request.data.get('confirmed') in [False, 'false', 'False']:
        new_status = 'cancelled'
    elif request.data.get('pending') in [True, 'true', 'True']:
        new_status = 'pending'
        
    if not new_status:
        return Response({
            "status": "error",
            "message": "You must provide a status toggle (e.g., 'ongoing': true, 'confirmed': true)",
            "body": {}
        }, status=400)

    try:
        booking = CarBooking.objects.get(booking_id=booking_id)
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        # Increment company total_bookings when they accept (confirm) the booking
        if new_status == 'confirmed' and old_status != 'confirmed':
            company = booking.car.companyid if booking.car else None
            if company:
                company.total_bookings = (company.total_bookings or 0) + 1
                company.save()
                
                if company.company_id and company.company_id.email:
                    from sevy_app.utils.email_service import send_notification_email
                    company_name = company.company_id.user_info.full_names if hasattr(company.company_id, 'user_info') else 'Partner'
                    send_notification_email(
                        to_email=company.company_id.email,
                        subject="Booking Confirmed!",
                        name=company_name,
                        message=f"The rental booking for your {booking.car.brand} {booking.car.name} has been confirmed.",
                    )
            
            # Notify the customer that booking was accepted
            from sevy_app.utils.fcm_service import send_fcm_notification
            Notification.objects.create(
                user=booking.user,
                title="Booking Accepted by Company",
                message=f"Your car rental booking has been accepted by the rental company!",
                notification_type='rental',
                related_id=booking.booking_id
            )
            car_image = booking.car.images[0] if booking.car and booking.car.images else None
            
            import threading
            def send_confirmed_notifications():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    from sevy_app.utils.email_service import send_notification_email
                    
                    # Notify Customer External
                    send_fcm_notification(
                        user=booking.user,
                        title="Booking Accepted by Company",
                        body="Your car rental booking has been accepted by the rental company!",
                        data={"type": "rental", "booking_id": str(booking.booking_id)},
                        image=car_image
                    )
                    if booking.user and booking.user.email:
                        customer_name = booking.user.user_info.full_names if hasattr(booking.user, 'user_info') else 'Customer'
                        send_notification_email(
                            to_email=booking.user.email,
                            subject="Booking Accepted",
                            name=customer_name,
                            message="Your car rental booking has been accepted by the rental company!",
                            details={
                                "Booking ID": booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id,
                                "Car": f"{booking.car.brand} {booking.car.name}" if booking.car else ""
                            },
                            action_text="View Booking",
                            action_url="https://sevymobility.com/rentals"
                        )
                    
                    # Notify Driver External
                    if booking.driver and booking.driver.userid:
                        send_fcm_notification(
                            user=booking.driver.userid,
                            title="Booking Accepted by Company",
                            body="The rental company has accepted the booking. Prepare for the upcoming trip.",
                            data={"type": "driverbooking", "booking_id": str(booking.booking_id)},
                            image=car_image
                        )
                        if hasattr(booking.driver.userid, 'email') and booking.driver.userid.email:
                            driver_name = booking.driver.userid.user_info.full_names if hasattr(booking.driver.userid, 'user_info') else 'Driver'
                            send_notification_email(
                                to_email=booking.driver.userid.email,
                                subject="Booking Accepted by Company",
                                name=driver_name,
                                message="The rental company has accepted the booking you are assigned to.",
                                details={
                                    "Booking ID": booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id
                                },
                                action_text="View Dashboard",
                                action_url="https://sevymobility.com"
                            )
                except Exception as e:
                    print(f"Error in send_confirmed_notifications: {e}")
                    
            threading.Thread(target=send_confirmed_notifications).start()
        if new_status == 'cancelled':
            Notification.objects.create(
                user=booking.user,
                title="Booking Cancelled",
                message=f"Your booking {booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id} has been cancelled.",
                notification_type="booking_cancelled",
                related_id=booking.booking_id
            )
            
            from sevy_app.utils.fcm_service import send_fcm_notification
            car_image = booking.car.images[0] if booking.car and booking.car.images else None
            
            # Synchronous Database Notifications
            if booking.driver and booking.driver.userid:
                Notification.objects.create(
                    user=booking.driver.userid,
                    title="Booking Cancelled",
                    message="The rental company has cancelled or rejected the booking you were assigned to.",
                    notification_type='driverbooking',
                    related_id=booking.booking_id
                )
                
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Booking Cancelled",
                    message=f"The rental booking for your {booking.car.brand} {booking.car.name} has been cancelled.",
                    notification_type="companybooking",
                    related_id=booking.booking_id
                )
                
            import threading
            def send_cancelled_notifications():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    from sevy_app.utils.email_service import send_notification_email
                    
                    # Notify Customer External
                    send_fcm_notification(
                        user=booking.user,
                        title="Booking Rejected",
                        body="Your car rental booking was rejected by the company.",
                        data={"type": "rental", "booking_id": str(booking.booking_id)},
                        image=car_image
                    )
                    if booking.user and booking.user.email:
                        customer_name = booking.user.user_info.full_names if hasattr(booking.user, 'user_info') else 'Customer'
                        send_notification_email(
                            to_email=booking.user.email,
                            subject="Booking Rejected",
                            name=customer_name,
                            message="Unfortunately, your car rental booking was rejected by the rental company.",
                            details={
                                "Booking ID": booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id
                            },
                            action_text="View Rentals",
                            action_url="https://sevymobility.com/rentals"
                        )
                        
                    # Notify Driver External
                    if booking.driver and booking.driver.userid:
                        send_fcm_notification(
                            user=booking.driver.userid,
                            title="Booking Cancelled",
                            body="The rental company has cancelled or rejected the booking.",
                            data={"type": "driverbooking", "booking_id": str(booking.booking_id)},
                            image=car_image
                        )
                        if hasattr(booking.driver.userid, 'email') and booking.driver.userid.email:
                            driver_name = booking.driver.userid.user_info.full_names if hasattr(booking.driver.userid, 'user_info') else 'Driver'
                            send_notification_email(
                                to_email=booking.driver.userid.email,
                                subject="Booking Cancelled",
                                name=driver_name,
                                message="The rental company has cancelled or rejected the booking you were assigned to.",
                                details={
                                    "Booking ID": booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id
                                },
                                action_text="View Dashboard",
                                action_url="https://sevymobility.com"
                            )
                            
                    # Notify Company External
                    if company_user:
                        send_fcm_notification(
                            user=company_user,
                            title="Booking Cancelled",
                            body=f"The rental booking for your {booking.car.brand} {booking.car.name} has been cancelled.",
                            data={"type": "companybooking", "booking_id": str(booking.booking_id)},
                            image=car_image
                        )
                        if hasattr(company_user, 'email'):
                            company_name = company_user.user_info.full_names if hasattr(company_user, 'user_info') else 'Partner'
                            send_notification_email(
                                to_email=company_user.email,
                                subject="Booking Cancelled",
                                name=company_name,
                                message=f"Unfortunately, the rental booking for your {booking.car.brand} {booking.car.name} has been cancelled.",
                                details={
                                    "Booking ID": booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id,
                                    "Status": "Cancelled"
                                },
                                action_text="View Dashboard",
                                action_url="https://sevymobility.com/dashboard"
                            )
                except Exception as e:
                    print(f"Error in send_cancelled_notifications: {e}")

            threading.Thread(target=send_cancelled_notifications).start()
            
            # Notify admins
            notify_admins(
                title="Booking Cancelled",
                message=f"Booking {getattr(booking, 'booking_number', None) or booking.booking_id} was cancelled.",
                notification_type="booking_cancelled",
                related_id=booking.booking_id
            )
        elif new_status == 'completed':
            company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
            if not company_user and booking.car and booking.car.companyid:
                company_user = getattr(booking.car.companyid, 'company_id', None)
                
            if company_user:
                Notification.objects.create(
                    user=company_user,
                    title="Booking Completed",
                    message=f"The rental booking for your {booking.car.brand} {booking.car.name} has been completed.",
                    notification_type="companytransaction",
                    related_id=booking.booking_id
                )
            import threading
            def send_completed_notifications():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    from sevy_app.utils.email_service import send_notification_email
                    car_image = booking.car.images[0] if booking.car and booking.car.images else None

                    if company_user:
                        send_fcm_notification(
                            user=company_user,
                            title="Booking Completed",
                            body=f"The rental booking for your {booking.car.brand} {booking.car.name} has been completed and payment has been processed.",
                            data={"type": "companytransaction", "booking_id": str(booking.booking_id)},
                            image=car_image
                        )
                        if hasattr(company_user, 'email'):
                            company_name = company_user.user_info.full_names if hasattr(company_user, 'user_info') else 'Partner'
                            send_notification_email(
                                to_email=company_user.email,
                                subject="Car Rental Booking Completed",
                                name=company_name,
                                message=f"The rental booking for your {booking.car.brand} {booking.car.name} has now been marked as completed. The payment will be available in your balance shortly.",
                                details={
                                    "Booking ID": booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id,
                                    "Status": "Completed"
                                },
                                action_text="View Dashboard",
                                action_url="https://sevymobility.com"
                            )
                            
                    # Email Customer
                    if booking.user and booking.user.email:
                        customer_name = booking.user.user_info.full_names if hasattr(booking.user, 'user_info') else 'Customer'
                        send_notification_email(
                            to_email=booking.user.email,
                            subject="Booking Completed",
                            name=customer_name,
                            message=f"Thank you for choosing Sevy Mobility! Your booking {booking.booking_number if hasattr(booking, 'booking_number') else booking.booking_id} has been successfully completed.",
                            action_text="Book Again",
                            action_url="https://sevymobility.com/rentals"
                        )
                except Exception as e:
                    print(f"Error in send_completed_notifications: {e}")

            threading.Thread(target=send_completed_notifications).start()
            # Notify Admins
            tx_type = "company_transaction" if company_user else "driver_transaction"
            try:
                notify_admins(
                    title="Booking Completion Request",
                    message=f"A completion request for booking {getattr(booking, 'booking_number', None) or booking.booking_id} requires your review and approval.",
                    notification_type=tx_type,
                    related_id=booking.booking_id
                )
            except Exception as e:
                print(f"\\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                print(f"Booking Completion Notification Error:\\n{str(e)}")
                print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\\n")
        
        return Response({
            "status": "success",
            "message": f"Booking status updated to {new_status}",
            "body": {
                "booking_id": booking.booking_id,
                "status": booking.status
            }
        }, status=200)

    except CarBooking.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Booking not found",
            "body": {}
        }, status=404)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "body": {}
        }, status=500)
