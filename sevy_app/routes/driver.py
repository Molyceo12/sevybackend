from django.urls import path
from ..views.driver.location_update import update_driver_location
from ..views.driver.find_nearest import find_nearest_driver
from ..views.driver.find_nearest_driver_only import find_nearest_driver_only
from ..views.driver.get_all import get_all_drivers
from ..views.driver.get_driver_incoming_trips import get_driver_incoming_trips
from ..views.driver.update_trip_status import update_trip_status
from ..views.driver.get_driver_all_trips import get_driver_all_trips
from ..views.driver.get_driver_trips_and_bookings import get_driver_trips_and_bookings
from ..views.driver.request_trip_completion import request_trip_completion
from ..views.driver.withdraw import withdraw
from ..views.driver.update_booking_driver_status import update_booking_driver_status
from ..views.driver.get_details import get_driver_details
from ..views.driver.toggle_availability import toggle_availability
from ..views.driver.update_documents import update_driver_documents
from ..views.driver.update_vehicle import update_driver_vehicle

urlpatterns = [
    path('location/update/', update_driver_location, name='update_driver_location'),
    path('location/nearest/', find_nearest_driver, name='find_nearest_driver'),
    path('driver_only/nearest/', find_nearest_driver_only, name='find_nearest_driver_only'),
    path('all/', get_all_drivers, name='get_all_drivers'),
    path('trips/incoming/', get_driver_incoming_trips, name='get_driver_incoming_trips'),
    path('trips/status/update/', update_trip_status, name='update_trip_status'),
    path('booking/updatedriverstatus/', update_booking_driver_status, name='update_booking_driver_status'),
    path('trips/all/', get_driver_all_trips, name='get_driver_all_trips'),
    path('trips_and_bookings/', get_driver_trips_and_bookings, name='get_driver_trips_and_bookings'),
    path('trips/request_completion/', request_trip_completion, name='request_trip_completion'),
    path('details/', get_driver_details, name='get_driver_details'),
    path('withdraw/', withdraw, name='driver_withdraw'),
    path('toggle_availability/', toggle_availability, name='toggle_availability'),
    path('<str:driver_id>/update-documents/', update_driver_documents, name='update_driver_documents'),
    path('<str:driver_id>/update-vehicle/', update_driver_vehicle, name='update_driver_vehicle'),
]
