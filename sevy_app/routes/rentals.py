from django.urls import path
from ..views.rentals import delete_car, get_all_cars, get_car, get_nearby_cars, like_car, unlike_car, check_like, search_cars, get_pricing_config

urlpatterns = [
    path('delete/', delete_car, name='delete_car'),
    path('all/', get_all_cars, name='get_all_cars'),
    path('get/<str:car_id>/', get_car, name='get_car'),
    path('nearby/', get_nearby_cars, name='get_nearby_cars'),
    path('like/<str:car_id>/', like_car, name='like_car'),
    path('unlike/<str:car_id>/', unlike_car, name='unlike_car'),
    path('check_like/<str:car_id>/<str:user_id>/', check_like, name='check_like'),
    path('search/', search_cars, name='search_cars'),
    path('pricing/', get_pricing_config, name='get_pricing_config'),
]
