from django.urls import path
from .views import (ProductListView,
                    ProductDetailSlugView,
                    ProductDownloadView,
                    ProductsInCategoryView,
                    ProductsByAuthorView)

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('category/<slug:slug>/', ProductsInCategoryView.as_view(), name='category'),
    path('author/<slug:slug>/', ProductsByAuthorView.as_view(), name='author'),
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='detail'),
    path('<slug:slug>/<int:pk>/', ProductDownloadView.as_view(), name='download'),
]
