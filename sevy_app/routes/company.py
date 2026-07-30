from django.urls import path
from sevy_app.views.company import get_company_bookings, get_company_transactions, get_company_requests, get_company_dashboard, get_company_cars, create_car, edit_car, get_latest_cars, withdraw, delete_company, register_company, review_company, update_company_documents
from sevy_app.views.company.get_explore import get_company_explore
from sevy_app.views.company.add_explore import add_company_explore
from sevy_app.views.company.delete_explore import delete_company_explore
from sevy_app.views.company.edit_explore import edit_company_explore

urlpatterns = [
    path('bookings/', get_company_bookings, name='get_company_bookings'),
    path('transactions/', get_company_transactions, name='get_company_transactions'),
    path('requests/', get_company_requests, name='get_company_requests'),
    path('getcompany/', get_company_dashboard, name='get_company_dashboard'),
    path('cars/', get_company_cars, name='get_company_cars'),
    path('explore/', get_company_explore, name='get_company_explore'),
    path('create-explore/', add_company_explore, name='create_company_explore'),
    path('delete-explore/', delete_company_explore, name='delete_company_explore'),
    path('edit-explore/', edit_company_explore, name='edit_company_explore'),
    path('create-car/', create_car, name='create_company_car'),
    path('edit-car/', edit_car, name='edit_company_car'),
    path('latest-cars/', get_latest_cars, name='get_latest_cars'),
    path('withdraw/', withdraw, name='withdraw'),
    path('delete/', delete_company, name='delete_company'),
    path('register/', register_company, name='register_company'),
    path('review/', review_company, name='review_company'),
    path('<str:company_id>/update-documents/', update_company_documents, name='update_company_documents'),
]
