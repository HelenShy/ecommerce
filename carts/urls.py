from django.urls import path
from .views import (cart_page, cart_update, checkout_page)

urlpatterns = [
    path('cart/', cart_page, name='cart'),
    path('update/', cart_update, name='update'),
    path('checkout/', checkout_page, name='checkout'),
]
