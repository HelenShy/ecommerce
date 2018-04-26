from django.urls import path
from .views import (cart_page, cart_update)

urlpatterns = [
    path('cart/', cart_page, name='cart'),
    path('update/', cart_update, name='update'),
]
