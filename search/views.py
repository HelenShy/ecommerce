from django.shortcuts import render
from django.views.generic  import ListView, DetailView

from products.models import Product
from carts.models import Cart


class SearchProductView(ListView):
    # queryset = Product.objects.all()
    template_name = 'search/view.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SearchProductView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        context['query'] = self.request.GET.get('q')
        return context

    def get_queryset(self):
        search_content = self.request.GET.get('q')
        if search_content:
            return Product.objects.search(search_content)
        else:
            return Product.objects.all()
