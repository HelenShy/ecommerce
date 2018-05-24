from django.shortcuts import render

from categories.models import Category, Collection
from products.models import Product


def home_page(request):
    context= {}
    collections = Collection.objects.show_on_home_page().all()
    for c in collections:
        print(c)
        for p in c.products.all():
            print(p.title)
    genres = [cat for cat in Category.objects.all()]
    context['collections'] = collections
    context['genres'] = genres
    return render(request, 'home.html', context)
