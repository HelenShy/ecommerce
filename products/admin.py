from django.contrib import admin

# Register your models here.

from .models import Product, ProductFile
from categories.models import Category, Collection


class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra = 1
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"


class CategoryInline(admin.TabularInline):
    model = Category.products.through


class CollectionInline(admin.TabularInline):
    model = Collection.products.through


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug']
    inlines = [ProductFileInline, CategoryInline, CollectionInline]
    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
