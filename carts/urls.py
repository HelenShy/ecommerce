from django.urls import path
from .views import (cart_page,
                    cart_update,
                    cart_api_update,
                    checkout_page,
                    CheckoutSuccessView)

urlpatterns = [
    path('', cart_page, name='cart'),
    path('update/', cart_update, name='update'),
    path('api-cart/', cart_api_update, name='api-cart'),
    path('checkout/', checkout_page, name='checkout'),
    path('checkout/success/', CheckoutSuccessView.as_view(), name='success')
]
