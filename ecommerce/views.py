from django.shortcuts import render

from categories.models import Category, Collection
from products.models import Product


def home_page(request):
    context= {}
    collections = {}
    collections['bestseller'] = Product.objects.by_collection('Bestseller')
    collections['children'] = Product.objects.by_collection('Children')
    collections['non_fiction'] = Product.objects.by_collection('Non fiction')
    genres = [cat for cat in Category.objects.all()]
    if request.user.is_authenticated:
        context['premium'] = "Secret"
    context['collections'] = collections
    context['genres'] = genres
    return render(request, 'home.html', context)
