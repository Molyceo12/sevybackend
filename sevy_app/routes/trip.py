from django.urls import path
from ..views.trip.create_trip import create_trip
from ..views.trip.get_details import get_trip_details
from ..views.trip.confirm_trip_completion import confirm_trip_completion
from ..views.trip.pay_trip import pay_trip
from ..views.trip.assign_driver import assign_driver


urlpatterns = [
    path('create/', create_trip, name='create_trip'),
    path('details/', get_trip_details, name='get_trip_details'),
    path('confirm_completion/', confirm_trip_completion, name='confirm_trip_completion'),
    path('pay/', pay_trip, name='pay_trip'),
    path('assign_driver/', assign_driver, name='assign_driver'),
]
