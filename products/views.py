from django.shortcuts import render
from django.views.generic  import ListView, DetailView

from .models import Product
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin

class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    model = Product
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context
