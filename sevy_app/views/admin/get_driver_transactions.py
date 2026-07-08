from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sevy_app.models import Transaction, Driver, Trip, CarBooking

@api_view(['GET'])
@permission_classes([AllowAny])
def get_driver_transactions(request):
    print("====== GET DRIVER TRANSACTIONS API HIT ======")
    try:
        # Fetch transactions strictly for drivers (user_type='driver')
        print("Fetching transactions for drivers...")
        transactions = Transaction.objects.filter(user__user_type='driver').select_related('user', 'user__driver_profile').order_by('-created_at')
        all_trips = Trip.objects.all().select_related('driverid', 'userid').order_by('-created_at')
        all_bookings = CarBooking.objects.all().select_related('car', 'driver', 'user').order_by('-created_at')
        
        trip_map = {t.trip_id: t for t in all_trips}
        booking_map = {b.booking_id: b for b in all_bookings}
        
        drivers = Driver.objects.all().select_related('userid')
        driver_map = {}
        for d in drivers:
            if d.userid_id:
                driver_map[d.userid_id] = d
            if d.userid and hasattr(d.userid, 'custom_id'):
                driver_map[d.userid.custom_id] = d
        
        processed_trip_ids = set()
        processed_booking_ids = set()
        transaction_list = []
        
        # 1. Process existing Transactions
        for t in transactions:
            driver_data = []
            driver_obj = None
            if t.user and hasattr(t.user, 'driver_profile') and t.user.driver_profile:
                driver_obj = t.user.driver_profile
            elif t.user_id and t.user_id in driver_map:
                driver_obj = driver_map[t.user_id]
                
            if driver_obj:
                name = driver_obj.full_name if (driver_obj.full_name and driver_obj.full_name.strip()) else (t.user.email if t.user else "Driver")
                driver_data.append({
                    "driver_id": getattr(driver_obj.userid, 'custom_id', str(driver_obj.userid_id)),
                    "full_name": name,
                    "phone_number": driver_obj.phone_number,
                    "vehicle_make_color": driver_obj.vehicle_make_color,
                    "plate_number": driver_obj.plate_number,
                    "balance": float(driver_obj.balance) if driver_obj.balance else 0.00
                })
                    
            booking_data = []
            if t.related_id:
                if t.transaction_type == 'cartripbooking' or t.related_id in trip_map:
                    trip = trip_map.get(t.related_id)
                    if trip:
                        # Only include trips that have been paid for
                        is_trip_paid = (trip.payment_status and trip.payment_status.lower() == 'paid') or (t.status and t.status.lower() in ['waitingapproval', 'approved', 'completed', 'paid', 'success'])
                        if is_trip_paid:
                            processed_trip_ids.add(trip.trip_id)
                            if not driver_data and trip.driverid:
                                d = trip.driverid
                                driver_data.append({
                                    "driver_id": getattr(d.userid, 'custom_id', str(d.userid_id)) if d.userid else '',
                                    "full_name": d.full_name,
                                    "phone_number": d.phone_number,
                                    "vehicle_make_color": d.vehicle_make_color,
                                    "plate_number": d.plate_number,
                                    "balance": float(d.balance) if d.balance else 0.00
                                })
                            booking_data.append({
                                "booking_id": trip.tracking_number if trip.tracking_number else trip.trip_id,
                                "booking_number": trip.tracking_number if trip.tracking_number else trip.trip_id,
                                "booking_type": "trip",
                                "status": trip.status,
                                "start_place": trip.start_place_name,
                                "destination": trip.destination_name,
                                "total_price": float(trip.total_price) if trip.total_price else 0.0,
                                "distance_km": trip.trip_distance_km
                            })
                if not booking_data and (t.transaction_type == 'carbooking' or t.related_id in booking_map):
                    booking = booking_map.get(t.related_id)
                    if booking:
                        # Only include bookings that have been paid for
                        is_booking_paid = (booking.payment_status and booking.payment_status.lower() == 'paid') or (t.status and t.status.lower() in ['waitingapproval', 'approved', 'completed', 'paid', 'success'])
                        if is_booking_paid:
                            processed_booking_ids.add(booking.booking_id)
                            if not driver_data and booking.driver:
                                d = booking.driver
                                driver_data.append({
                                    "driver_id": getattr(d.userid, 'custom_id', str(d.userid_id)) if d.userid else '',
                                    "full_name": d.full_name,
                                    "phone_number": d.phone_number,
                                    "vehicle_make_color": d.vehicle_make_color,
                                    "plate_number": d.plate_number,
                                    "balance": float(d.balance) if d.balance else 0.00
                                })
                            booking_data.append({
                                "booking_id": booking.booking_id,
                                "booking_number": getattr(booking, 'booking_number', booking.booking_id),
                                "booking_type": "car_rental",
                                "status": booking.status,
                                "pickup_location": booking.pickup_location,
                                "dropoff_location": booking.dropoff_location,
                                "pickup_date": str(booking.start_date) if booking.start_date else None,
                                "return_date": str(booking.end_date) if booking.end_date else None,
                                "total_price": float(booking.total_price) if booking.total_price else 0.0,
                                "car_name": f"{booking.car.brand} {booking.car.name}" if booking.car else "Unknown",
                                "car_image": booking.car.images[0] if isinstance(booking.car.images, list) and len(booking.car.images) > 0 else (booking.car.images if isinstance(booking.car.images, str) else None)
                            })
            
            if not booking_data:
                continue

            transaction_dict = {
                "transaction_id": t.transaction_id,
                "transaction_type": t.transaction_type,
                "amount": float(t.amount) if t.amount else 0.00,
                "currency": t.currency,
                "status": t.status,
                "customer_approved": t.customer_approved,
                "driver_email": t.user.email if t.user else "Unknown",
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "driver": driver_data,
            }
            
            if t.transaction_type == 'cartripbooking' or (booking_data and booking_data[0].get('booking_type') == 'trip'):
                transaction_dict["trip"] = booking_data
            else:
                transaction_dict["booking"] = booking_data
                
            transaction_list.append(transaction_dict)

        def priority_score(tx):
            item_status = ''
            if tx.get('trip') and len(tx['trip']) > 0:
                item_status = str(tx['trip'][0].get('status', '')).lower()
            elif tx.get('booking') and len(tx['booking']) > 0:
                item_status = str(tx['booking'][0].get('status', '')).lower()
                
            is_completed_item = item_status in ['completed', 'paid', 'confirmed']
            
            if is_completed_item:
                return 0
            return 1

        # Sort by date descending first, then by priority score ascending (stable sort)
        transaction_list.sort(key=lambda x: str(x.get('created_at') or ''), reverse=True)
        transaction_list.sort(key=priority_score)

        return Response({
            "code": 200,
            "status": True,
            "message": "Driver transactions retrieved successfully.",
            "total_transactions": len(transaction_list),
            "body": transaction_list
        }, status=200)
        
    except Exception as e:
        print(f"====== ERROR IN GET DRIVER TRANSACTIONS: {str(e)} ======")
        import traceback
        traceback.print_exc()
        return Response({
            "code": 500,
            "status": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
