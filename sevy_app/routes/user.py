from django.urls import path
from sevy_app.views.user import MostSearchedPlacesView, get_notifications, get_user, delete_account, get_user_trips, get_user_bookings, logout, has_unread_notifications
from sevy_app.views.user.get_pending_approvals import get_pending_approvals
from sevy_app.views.user.mark_notification_read import mark_notification_read
from sevy_app.views.user.delete_notification import delete_notification
from sevy_app.views.user.update_fcm_token import update_fcm_token

urlpatterns = [
    path('most-searched/', MostSearchedPlacesView.as_view(), name='user_most_searched'),
    path('notifications/', get_notifications, name='get_notifications'),
    path('getUser/', get_user, name='get_user'),
    path('delete/', delete_account, name='delete_account'),
    path('trips/', get_user_trips, name='get_user_trips'),
    path('bookings/', get_user_bookings, name='get_user_bookings'),
    path('logout/', logout, name='logout'),
    path('pending_approvals/', get_pending_approvals, name='get_pending_approvals'),
    path('notifications/read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/', delete_notification, name='delete_notification'),
    path('notifications/has-unread/', has_unread_notifications, name='has_unread_notifications'),
    path('fcm-token/', update_fcm_token, name='update_fcm_token'),
]

