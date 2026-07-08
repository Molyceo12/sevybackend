from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import CarBooking, CustomUser, Driver, Car, Notification
from sevy_app.utils.notifications import notify_admins
import datetime

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    try:
        userid_val = request.data.get('userid')
        car_id_val = request.data.get('car_id')
        driverid_val = request.data.get('driverid')
        
        booking_type = request.data.get('booking_type')
        client_sex = request.data.get('client_sex', 'any')
        rental_plan = request.data.get('rental_plan')
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        pickup_location = request.data.get('pickup_location')
        dropoff_location = request.data.get('dropoff_location')
        total_price = request.data.get('total_price')

        # Basic validation for essential fields
        if not all([userid_val, car_id_val, booking_type, rental_plan, start_date, end_date, pickup_location, dropoff_location, total_price]):
            return Response({
                "code": 400,
                "status": False,
                "message": "Missing required fields.",
                "body": {}
            }, status=400)
            
        user = CustomUser.objects.filter(custom_id=userid_val).first()
        if not user:
             return Response({
                "code": 404,
                "status": False,
                "message": "Customer not found.",
                "body": {}
            }, status=404)
            
        car = Car.objects.filter(car_id=car_id_val).first()
        if not car:
             return Response({
                "code": 404,
                "status": False,
                "message": "Car not found.",
                "body": {}
            }, status=404)

        driver = None
        if booking_type == 'with_driver' and driverid_val:
            # Fetch the driver profile if they selected a specific driver
            driver = Driver.objects.filter(userid__custom_id=driverid_val).first()
            if not driver:
                 return Response({
                    "code": 404,
                    "status": False,
                    "message": "Driver not found.",
                    "body": {}
                }, status=404)

        driver_status = 'waiting' if (booking_type == 'with_driver' and driver) else None

        # Create the booking record
        booking = CarBooking.objects.create(
            user=user,
            car=car,
            companyid=car.companyid,
            driver=driver,
            booking_type=booking_type,
            client_sex=client_sex,
            rental_plan=rental_plan,
            start_date=start_date,
            end_date=end_date,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            total_price=float(total_price),
            status='pending',
            driver_status=driver_status,
            payment_status='unpaid'
        )
        
        # Create a notification for the driver if one was selected
        if driver and driver.userid:
            from sevy_app.models import Notification
            Notification.objects.create(
                user=driver.userid,
                title="New Driving Assignment",
                message=f"You have been requested to drive a {car.brand} {car.name} from {start_date} to {end_date}.",
                notification_type='rental',
                related_id=booking.booking_id
            )
            
            # Start the 2-minute timeout task
            from sevy_app.tasks import booking_timeout_task
            booking_timeout_task.apply_async((booking.booking_id,), countdown=120)

        # Notify the customer
        from sevy_app.models import Notification
        Notification.objects.create(
            user=booking.user,
            title="Booking Request Submitted",
            message=f"Your booking request for a {car.brand} {car.name} has been submitted.",
            notification_type='rental',
            related_id=booking.booking_id
        )
        
        # Notify the company
        company_user = getattr(booking.companyid, 'company_id', None) if booking.companyid else None
        if not company_user and car.companyid:
            company_user = getattr(car.companyid, 'company_id', None)
            
        if company_user:
            Notification.objects.create(
                user=company_user,
                title="New Booking Request",
                message=f"A new booking request has been made for your {car.brand} {car.name} from {start_date} to {end_date}.",
                notification_type='rental',
                related_id=booking.booking_id
            )
            
        # Notify admins
        notify_admins(
            title="New Booking Request",
            message=f"New booking request for {car.brand} {car.name} from {start_date} to {end_date}.",
            notification_type='rental',
            related_id=booking.booking_id
        )
        
        return Response({
            "code": 201,
            "status": True,
            "message": "Car booking created successfully.",
            "body": {
                "booking_id": booking.booking_id,
                "status": booking.status,
                "payment_status": booking.payment_status,
                "created_at": booking.created_at,
                "total_price": booking.total_price
            }
        }, status=201)

    except ValueError:
        return Response({
            "code": 400,
            "status": False,
            "message": "Invalid format for price or dates.",
            "body": {}
        }, status=400)
    except Exception as e:
        return Response({
            "code": 500,
            "status": False,
            "message": f"Server error: {str(e)}",
            "body": {}
        }, status=500)
