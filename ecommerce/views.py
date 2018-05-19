from django.shortcuts import render

from categories.models import Category, Collection
from products.models import Product


def home_page(request):
    context= {}
    collections = {}
    data = [{'ctx_name':'bestseller', 'title':'Bestseller'},
            {'ctx_name':'children', 'title':'Children'},
            {'ctx_name':'non_fiction', 'title':'Non fiction'},]
    for coll_data in data:
        collections[coll_data['ctx_name']] = Product.objects.by_collection(
            coll_data['title'])
    genres = [cat for cat in Category.objects.all()]
    context['collections'] = collections
    context['genres'] = genres
    return render(request, 'home.html', context)
