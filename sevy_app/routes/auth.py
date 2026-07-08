from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from sevy_app.views.auth.customer_register import CustomerRegistrationView
from sevy_app.views.auth.driver_register import DriverRegistrationView
from sevy_app.views.auth.login import LoginView

urlpatterns = [
    path('register/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('register-driver/', DriverRegistrationView.as_view(), name='register-driver'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
