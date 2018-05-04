from django.urls import path
from .views import (payment_page, payment_create_page)

urlpatterns = [
    path('payment/', payment_page, name='payment'),
    path('payment/create/', payment_create_page, name='payment-endpoint'),
]
