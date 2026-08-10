import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sevy.settings')

app = Celery('sevy')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from celery.signals import worker_ready

@worker_ready.connect
def recover_pending_trips(sender, **kwargs):
    # Important: Import models inside the signal handler so Django apps are fully loaded
    try:
        from sevy_app.models import Trip
        from sevy_app.tasks import trip_timeout_task
        from django.utils import timezone
        
        print("\n=========================================================")
        print("Celery Worker Ready: Recovering Pending Trips...")
        print("=========================================================")
        
        # 1. Recover trips waiting for driver acceptance (2 mins timeout)
        waiting_trips = Trip.objects.filter(status='upcoming', driver_status='waiting')
        for trip in waiting_trips:
            time_elapsed = (timezone.now() - trip.created_at).total_seconds()
            remaining_time = max(0, 1800 - int(time_elapsed))
            
            print(f"Recovering waiting Trip {trip.trip_id} - Scheduled in {remaining_time}s")
            if remaining_time >= 0:
                trip_timeout_task.apply_async((trip.trip_id, 'waiting'), countdown=remaining_time)
                
        # 2. Re-schedule 'ready' timeouts (15 minutes limit)
        active_ready = Trip.objects.filter(driver_status='ready', status__in=['upcoming', 'active'])
        for trip in active_ready:
            time_passed = (now - trip.created_at).total_seconds()
            remaining_time = max(900 - int(time_passed), 0) # 15 minutes limit for ready
            
            print(f"Recovering ready Trip {trip.trip_id} - Scheduled in {remaining_time}s")
            if remaining_time >= 0:
                trip_timeout_task.apply_async((trip.trip_id, 'ready'), countdown=remaining_time)
                
        # 3. Re-schedule car booking driver timeouts
        active_bookings = CarBooking.objects.filter(status='pending', driver__isnull=False)
        for booking in active_bookings:
            time_passed = (now - booking.created_at).total_seconds()
            remaining_time = max(1800 - int(time_passed), 0) # 30 minutes limit
            
            print(f"Recovering pending Booking {booking.booking_id} - Scheduled in {remaining_time}s")
            if remaining_time >= 0:
                booking_timeout_task.apply_async((booking.booking_id,), countdown=remaining_time)

        # 4. Recover pending trip completions (7 mins timeout)
        pending_completions = Trip.objects.filter(approval_status='requestsent')
        for trip in pending_completions:
            base_time = trip.updated_at if trip.updated_at else trip.created_at
            time_elapsed = (timezone.now() - base_time).total_seconds()
            remaining_time = max(0, 420 - int(time_elapsed))
            
            print(f"Recovering pending Trip Completion {trip.trip_id} - Scheduled in {remaining_time}s")
            try:
                auto_accept_trip_completion_task.apply_async((trip.trip_id,), countdown=remaining_time)
            except Exception as e:
                print(f"Failed to recover Trip Completion {trip.trip_id}: {e}")


        print("=========================================================\n")
    except Exception as e:
        print(f"Error during Celery startup recovery: {e}")


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
