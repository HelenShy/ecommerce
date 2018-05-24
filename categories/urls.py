from django.urls import path
from .views import (CategoriesAjaxView, CollectionListView)

urlpatterns = [
    path('data/', CategoriesAjaxView.as_view(), name='ajax-list'),
    path('collections/', CollectionListView.as_view(), name='collection-list'),
]
