from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import threading
from sevy_app.models import Transaction, Notification, PlatformCommission, Trip, CarBooking

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_transaction(request):
    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print("STARTING REJECT TRANSACTION API")
    print(f"Request data: {request.data}")
    
    if not request.user.is_superuser:
        print("Error: User is not superuser")
        return Response({
            "status": "error",
            "message": "Only admins can perform this action.",
            "body": {}
        }, status=403)

    transaction_id = request.data.get('transaction_id')
    print(f"Transaction ID: {transaction_id}")
    if not transaction_id:
        print("Error: Transaction ID missing")
        return Response({"status": "error", "message": "transaction_id is required", "body": {}}, status=400)

    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        print(f"Transaction found: {transaction}")
    except Transaction.DoesNotExist:
        print("Error: Transaction not found")
        return Response({"status": "error", "message": "Transaction not found", "body": {}}, status=404)

    if transaction.status not in ['waitingapproval', 'wait_approval']:
        print(f"Error: Transaction status is {transaction.status}")
        return Response({"status": "error", "message": f"Transaction cannot be rejected because its status is '{transaction.status}'", "body": {}}, status=400)

    # 1. Update status to rejected
    print("Updating transaction status...")
    transaction.status = 'rejected'
    transaction.completed_at = timezone.now()
    transaction.save()
    print("Transaction status updated.")

    # 2. Update status to failed in PlatformCommission table
    print("Updating PlatformCommission status...")
    PlatformCommission.objects.filter(transaction=transaction).update(status='failed')
    print("PlatformCommission status updated.")

    # Refund logic
    print("Starting refund logic...")
    user = transaction.user
    recipient_type = "User"
    if user:
        print(f"User found: {getattr(user, 'user_id', getattr(user, 'id', 'Unknown'))}")
        if hasattr(user, 'company_profile'):
            print("User is a company")
            company = user.company_profile
            # Refund to company balance if it was a withdrawal
            if transaction.transaction_type == 'withdrawal':
                print("Refunding withdrawal to company balance")
                company.balance += transaction.amount
                company.save()
            else:
                print("Not a withdrawal, skipping company refund")
            
            recipient_type = "Company"
            
            image_url = None
            booking = None
            if transaction.related_id:
                booking = CarBooking.objects.filter(booking_id=transaction.related_id).first()
            if not booking:
                booking = CarBooking.objects.filter(transaction=transaction).first()
                
            if booking:
                booking.admin_company_approval = 'denied'
                if not booking.driver:
                    booking.status = 'cancelled'
                elif booking.admin_driver_approval in ['denied', 'cancelled']:
                    booking.status = 'cancelled'
                booking.save()
            if booking and booking.car and getattr(booking.car, 'images', None):
                image_url = booking.car.images[0] if isinstance(booking.car.images, list) and len(booking.car.images) > 0 else None
            
            # Notify the company
            booking_ref = transaction.tracking_number if getattr(transaction, 'tracking_number', None) else ""
            msg_text = f"Your booking {booking_ref} payment request has been rejected.".replace("  ", " ")
            
            Notification.objects.create(
                user=user,
                title="Payout Rejected",
                message=msg_text,
                notification_type="companytransaction",
                related_id=transaction.transaction_id
            )
            

            def send_company_alerts():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    send_fcm_notification(
                        user=user,
                        title="Payout Rejected",
                        body=msg_text,
                        data={"type": "companytransaction", "transaction_id": str(transaction.transaction_id)},
                        image=None
                    )
                    
                    # Email the company
                    if hasattr(user, 'email') and user.email:
                        from sevy_app.utils.email_service import send_notification_email
                        company_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Partner'
                        send_notification_email(
                            to_email=user.email,
                            subject="Transaction Rejected",
                            name=company_name,
                            message=f"Your transaction of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                            details={
                                "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                                "Amount": f"{transaction.amount} {transaction.currency}",
                                "Status": "Rejected",
                                "Resolution": "The amount has been refunded to your account balance."
                            },
                            action_text="Contact Support",
                            action_url="mailto:support@sevymobility.com"
                        )
                except Exception as e:
                    print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Error in send_company_alerts:")
                    print(f"{str(e)}")
                    print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
            
            threading.Thread(target=send_company_alerts).start()

        elif hasattr(user, 'driver_profile'):
            print("User is a driver")
            driver = user.driver_profile
            # Refund to driver balance if it was a withdrawal
            if transaction.transaction_type == 'withdrawal':
                print("Refunding withdrawal to driver balance")
                driver.balance += transaction.amount
                driver.save()
            else:
                print("Not a withdrawal, skipping driver refund")
                
            recipient_type = "Driver"
            
            image_url = None
            print(f"Checking car booking... transaction.related_id='{transaction.related_id}'")
            try:
                booking = None
                if transaction.related_id:
                    booking = CarBooking.objects.filter(booking_id=transaction.related_id).first()
                if not booking:
                    booking = CarBooking.objects.filter(transaction=transaction).first()
                
                print(f"Booking: {booking}")
                if booking:
                    booking.admin_driver_approval = 'denied'
                    if booking.admin_company_approval in ['denied', 'cancelled']:
                        booking.status = 'cancelled'
                    booking.save()
                if booking and booking.car and getattr(booking.car, 'images', None):
                    image_url = booking.car.images[0] if isinstance(booking.car.images, list) and len(booking.car.images) > 0 else None
            except Exception as e:
                print(f"Error accessing car_bookings: {e}")
                
            print("Checking trips...")
            try:
                trip = None
                if transaction.related_id:
                    trip = Trip.objects.filter(trip_id=transaction.related_id).first()
                if not trip:
                    trip = Trip.objects.filter(transaction=transaction).first()
                
                print(f"Trip: {trip}")
                if trip:
                    trip.approval_status = 'denied'
                    trip.status = 'cancelled'
                    trip.save()
            except Exception as e:
                print(f"Error accessing trips: {e}")
            
            # Notify the driver
            print("Creating notification...")
            booking_ref = transaction.tracking_number if getattr(transaction, 'tracking_number', None) else ""
            msg_text = f"Your booking {booking_ref} payment request has been rejected.".replace("  ", " ")
            
            Notification.objects.create(
                user=user,
                title="Payout Rejected",
                message=msg_text,
                notification_type="drivertransaction",
                related_id=transaction.transaction_id
            )
            print("Notification created.")
            
            def send_driver_alerts():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    send_fcm_notification(
                        user=user,
                        title="Payout Rejected",
                        body=msg_text,
                        data={"type": "drivertransaction", "transaction_id": str(transaction.transaction_id)},
                        image=image_url
                    )
                    
                    # Email the driver
                    if hasattr(user, 'email') and user.email:
                        from sevy_app.utils.email_service import send_notification_email
                        driver_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Driver'
                        send_notification_email(
                            to_email=user.email,
                            subject="Transaction Rejected",
                            name=driver_name,
                            message=f"Your transaction of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                            details={
                                "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                                "Amount": f"{transaction.amount} {transaction.currency}",
                                "Status": "Rejected",
                                "Resolution": "The amount has been refunded to your account balance."
                            },
                            action_text="Contact Support",
                            action_url="mailto:support@sevymobility.com"
                        )
                except Exception as e:
                    print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Error in send_driver_alerts:")
                    print(f"{str(e)}")
                    print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
                    
            threading.Thread(target=send_driver_alerts).start()
            print("Driver alerts thread started.")

        else:
            print("User is a customer")
            recipient_type = "Customer"
            
            # Notify the customer
            print("Creating customer notification...")
            Notification.objects.create(
                user=user,
                title="Transaction Rejected",
                message=f"Your transaction of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                notification_type="transaction",
                related_id=transaction.transaction_id
            )
            print("Customer notification created.")
            

            def send_customer_alerts():
                try:
                    from sevy_app.utils.fcm_service import send_fcm_notification
                    send_fcm_notification(
                        user=user,
                        title="Transaction Rejected",
                        body="Your transaction has been rejected. The amount has been refunded.",
                        data={"type": "transaction", "transaction_id": str(transaction.transaction_id)}
                    )
                    
                    # Email the customer
                    if hasattr(user, 'email') and user.email:
                        from sevy_app.utils.email_service import send_notification_email
                        customer_name = user.user_info.full_names if hasattr(user, 'user_info') else 'Customer'
                        send_notification_email(
                            to_email=user.email,
                            subject="Transaction Rejected",
                            name=customer_name,
                            message=f"Your transaction of {transaction.amount} {transaction.currency} could not be processed and has been rejected.",
                            details={
                                "Transaction ID": transaction.tracking_number if getattr(transaction, 'tracking_number', None) else transaction.transaction_id,
                                "Amount": f"{transaction.amount} {transaction.currency}",
                                "Status": "Rejected",
                                "Resolution": "Please contact support if you need assistance."
                            },
                            action_text="Contact Support",
                            action_url="mailto:support@sevymobility.com"
                        )
                except Exception as e:
                    print(f"\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
                    print(f"Error in send_customer_alerts:")
                    print(f"{str(e)}")
                    print(f"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
            
            threading.Thread(target=send_customer_alerts).start()
            print("Customer alerts thread started.")

    # Notify the admin
    print("Creating admin notification...")
    Notification.objects.create(
        user=request.user,
        title="Transaction Rejected",
        message=f"{recipient_type} transaction {transaction.transaction_id} for {transaction.amount} {transaction.currency} was rejected.",
        notification_type="transaction",
        related_id=transaction.transaction_id
    )
    print("Admin notification created.")
    
    print("END OF REJECT TRANSACTION API")
    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    return Response({
        "status": "success",
        "message": "Transaction rejected successfully.",
        "body": {
            "transaction_id": transaction.transaction_id,
            "new_status": transaction.status
        }
    }, status=200)
