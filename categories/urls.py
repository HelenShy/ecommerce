from django.urls import path
from .views import (CategoriesAjaxView)

urlpatterns = [
    path('data/', CategoriesAjaxView.as_view(), name='ajax-list'),
]
