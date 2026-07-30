from django.urls import path
from ..views.bookings import create_booking, pay_booking, get_booking_details, update_booking_status, search_bookings, approve_completion, request_customer_approval

urlpatterns = [
    path('create/', create_booking, name='create_booking'),
    path('pay/', pay_booking, name='pay_booking'),
    path('approve-completion/', approve_completion, name='approve_completion'),
    path('details/', get_booking_details, name='get_booking_details'),
    path('update-status/', update_booking_status, name='update_booking_status'),
    path('search/', search_bookings, name='search_bookings'),
    path('request-customer-approval/', request_customer_approval, name='request_customer_approval'),
]
