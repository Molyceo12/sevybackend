"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import os

env = os.environ.get('ENV', 'test')
api_prefix = f'api/{env}/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(api_prefix, include('sevy_app.routes.auth')),
    path(f'{api_prefix}places/', include('sevy_app.routes.places')),
    path(f'{api_prefix}user/', include('sevy_app.routes.user')),
    path(f'{api_prefix}driver/', include('sevy_app.routes.driver')),
    path(f'{api_prefix}trip/', include('sevy_app.routes.trip')),
    path(f'{api_prefix}transaction/', include('sevy_app.routes.transaction')),
    path(f'{api_prefix}rentals/', include('sevy_app.routes.rentals')),
    path(f'{api_prefix}bookings/', include('sevy_app.routes.bookings')),
    path(f'{api_prefix}company/', include('sevy_app.routes.company')),
    path(f'{api_prefix}admin/', include('sevy_app.routes.admin')),
]
