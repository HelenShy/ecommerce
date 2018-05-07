from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime

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
        return products_viewed


class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(SalesView, self).dispatch(*args, **kwargs)
        return render(self.request, "400.html", {})

    def get_context_data(self, *args, **kwargs):
        now = timezone.now()
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        orders = Order.objects.all()
        context['last_orders'] = orders
        context['last_orders_totals'] = orders.totals_data()
        context['last_orders_cart_data'] = orders.totals_cart_data()
        context['last_paid_orders'] = orders.filter(status='paid')
        context['last_paid_orders_totals'] = orders.filter(
            status='paid').totals_data()
        return context
