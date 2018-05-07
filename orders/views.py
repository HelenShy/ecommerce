from django.shortcuts import render
from django.views.generic  import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .models import Order


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'orders/list.html'

    def get_queryset(self):
        qs = Order.objects.by_billing_profile(self.request)
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    queryset = Order.objects.all()
    template_name = 'orders/detail.html'

    def get_object(self):
        qs = Order.objects.by_billing_profile(
            self.request
        ).filter(order_id=self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        else:
            return Http404
