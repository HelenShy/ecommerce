from django.contrib import admin

# Register your models here.

from .models import Product, ProductFile


class ProductFileInline(admin.TabularInline):
    model = ProductFile
    extra = 1    
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug']
    inlines = [ProductFileInline]
    class Meta:
        model = Product

admin.site.register(Product, ProductAdmin)
