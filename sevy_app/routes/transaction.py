from django.urls import path
from ..views.transaction.create import create_transaction
from ..views.transaction.get_details import get_transaction_details

urlpatterns = [
    path('create/', create_transaction, name='create_transaction'),
    path('details/', get_transaction_details, name='get_transaction_details'),
]
