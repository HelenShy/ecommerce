from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
import datetime
from django.http import JsonResponse
import operator

from carts.models import Cart
from products.models import Product
from orders.models import Order


class ProductsHistoryView(LoginRequiredMixin, ListView):
    template_name = 'analytics/products_history.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductsHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        user = request.user
        products_viewed = user.objectviewed_set.by_model(Product)
        ordered = products_viewed.order_by('-changed', '-created')[:15]
        return ordered


class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(SalesView, self).dispatch(*args, **kwargs)
        return render(self.request, "400.html", {})

    def get_context_data(self, *args, **kwargs):
        now = timezone.now()
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        qs = Order.objects.all()
        context['today'] = qs.by_time_range(now).get_sales_breakdown()
        context['week'] = qs.by_week_range(1).get_sales_breakdown()
        context['4weeks'] = qs.by_week_range(4).get_sales_breakdown()
        context['current_month'] = qs.by_month().get_sales_breakdown()
        return context


class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            data = {}
            qs = Order.objects.all()
            if self.request.GET.get('type') == 'week':
                labels, totals = qs.period_totals('day', 7)
            if self.request.GET.get('type') == '4weeks':
                labels, totals = qs.period_totals('week', 4)
            data['labels'] = labels
            data['data'] = totals
        return JsonResponse(data)
