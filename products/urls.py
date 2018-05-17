from django.urls import path
from .views import (ProductListView,
                    ProductDetailSlugView,
                    ProductDownloadView,
                    ProductsInCategoryView)

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('category/<str:category>/', ProductsInCategoryView.as_view(), name='category'),
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='detail'),
    path('<slug:slug>/<int:pk>/', ProductDownloadView.as_view(), name='download'),
]
