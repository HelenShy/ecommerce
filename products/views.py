from django.shortcuts import render, redirect
from django.views.generic  import ListView, DetailView, View
from django.http import Http404, HttpResponse
from django.conf import settings
from django.contrib import messages
from wsgiref.util import FileWrapper
from mimetypes import guess_type
import os


from products.models import Product, ProductFile
from orders.models import ProductPurchase
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin
from categories.models import Category, Author

class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        context['title'] = 'All books'
        return context


class ProductsInCategoryView(ListView):
    template_name = 'products/list.html'

    def get_queryset(self):
        category = Category.objects.get(slug=self.kwargs.get('slug'))
        qs =  Product.objects.by_category(category.title)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(ProductsInCategoryView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        category = Category.objects.get(slug=self.kwargs.get('slug'))
        context['title'] = category.title
        return context


class ProductsByAuthorView(ListView):
    template_name = 'products/list.html'

    def get_queryset(self):
        author = Author.objects.get(slug=self.kwargs.get('slug'))
        qs =  Product.objects.by_author(author.name)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(ProductsByAuthorView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        author = Author.objects.get(slug=self.kwargs.get('slug'))
        context['title'] = author.name
        return context


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = 'products/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        cart_obj, cart_created = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context


class ProductDownloadView(View):
    def get(self, *args, **kwargs):
        slug = kwargs.get('slug')
        pk = kwargs.get('pk')
        downloads = ProductFile.objects.filter(pk=pk, product__slug=slug)
        if downloads.count() != 1:
            raise Http404("Downloads not found")
        download_obj = downloads.first()
        download_accessable = download_obj.free
        if not download_accessable:
            purchases = ProductPurchase.objects.products_by_request(self.request)
            if download_obj.product in purchases:
                download_accessable = True
            else:
                messages.error(self.request, "You do not have access to download this file.")
                return redirect(download_obj.get_default_url())
        file_root = settings.PROTECTED_ROOT
        filepath = download_obj.file.path
        final_filepath = os.path.join(file_root, filepath)
        with open(filepath, 'rb') as f:
            wrapper = FileWrapper(f)
            mimetype = 'application/force-download'
            guessed_mimetype = guess_type(filepath)[0]
            if guessed_mimetype:
                mimetype = guessed_mimetype
            resp = HttpResponse(wrapper, content_type=mimetype)
            resp['Content-Disposition'] = "attachment;filename=%s" %(download_obj.name)
            resp["X-SendFile"] = str(download_obj.name)
            return resp
