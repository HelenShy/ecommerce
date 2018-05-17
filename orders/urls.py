from django.urls import path
from .views import (OrderListView,
                    OrderDetailView,
                    VerifyOwnershipView)

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('verify/ownership/', VerifyOwnershipView.as_view(), name='verify-ownership'),
    path('<order_id>/', OrderDetailView.as_view(), name='detail'),
]
