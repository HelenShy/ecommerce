from django.shortcuts import render
from django.views.generic  import ListView, DetailView, View
from django.http import Http404, HttpResponse
from django.conf import settings
from wsgiref.util import FileWrapper
from mimetypes import guess_type
import os

from .models import Product, ProductFile
from carts.models import Cart
from analytics.mixins import ObjectViewedMixin


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'products/list.html'


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
            print(download_obj.name)
            resp["X-SendFile"] = str(download_obj.name)
            return resp
