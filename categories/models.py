from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import Q

from products.models import Product
from ecommerce.utils import unique_slug_generator


class Category(models.Model):
    title = models.CharField(max_length=1200)
    slug = models.SlugField(blank=True, unique=True)
    active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Returns category`s url.
        """
        return reverse("products:category", kwargs={'category': self.title})

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


def pre_save_category_add_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(pre_save_category_add_slug, sender=Category)


class Collection(models.Model):
    title = models.CharField(max_length=1200)
    slug = models.SlugField(blank=True, unique=True)
    active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


def pre_save_collection_add_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(pre_save_collection_add_slug, sender=Collection)
