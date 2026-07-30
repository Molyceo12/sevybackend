from django.urls import path
from sevy_app.views.admin import get_companies, get_users, get_drivers, get_revenue, get_requests, get_company_requests, get_company_transactions, admin_profile, get_driver_requests, get_driver_transactions, get_admin_dashboard, approve_transaction, reject_transaction, review_driver_request, get_platform_finance, manage_system_config, approve_withdrawal, reject_withdrawal
from sevy_app.views.admin.get_user_context import get_user_context

urlpatterns = [
    path('context-data/', get_user_context, name='admin_get_user_context'),
    path('dashboard/', get_admin_dashboard, name='admin_dashboard'),
    path('profile/', admin_profile, name='admin_profile'),
    path('companies/', get_companies, name='admin_get_companies'),
    path('users/', get_users, name='admin_get_users'),
    path('drivers/', get_drivers, name='admin_get_drivers'),
    path('driver/requests/', get_driver_requests, name='admin_driver_requests'),
    path('driver/requests/review/', review_driver_request, name='admin_review_driver_request'),
    path('driver/payments/', get_driver_transactions, name='admin_driver_payments'),
    path('revenue/', get_revenue, name='admin_get_revenue'),
    path('requests/', get_requests, name='admin_get_requests'),
    path('company/requests/', get_company_requests, name='admin_company_requests'),
    path('company/payments/', get_company_transactions, name='admin_company_payments'),
    path('transactions/approve/', approve_transaction, name='admin_approve_transaction'),
    path('transactions/reject/', reject_transaction, name='admin_reject_transaction'),
    path('withdrawals/approve/', approve_withdrawal, name='admin_approve_withdrawal'),
    path('withdrawals/reject/', reject_withdrawal, name='admin_reject_withdrawal'),
    path('finance/', get_platform_finance, name='admin_get_platform_finance'),
    path('config/', manage_system_config, name='admin_system_config'),
]
