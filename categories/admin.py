from django.contrib import admin

from .models import Category, Collection, Author


admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(Author)
