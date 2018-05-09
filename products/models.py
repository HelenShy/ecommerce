from django.db import models
import random
import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from ecommerce.utils import unique_slug_generator, get_filename


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    new_filename = random.randint(1, 5000000000)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(
        new_filename=new_filename,
        ext=ext
    )
    return 'products/{new_filename}/{final_filename}'.format(
        new_filename=new_filename,
        final_filename=final_filename
    )


class ProductManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(category__title__icontains=query))
        return self.get_queryset().filter(lookups).distinct()


class Product(models.Model):
    title = models.CharField(max_length=1200)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = ProductManager()
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={'slug': self.slug})

    @property
    def name(self):
        return self.title

    def get_downloads(self):
        qs = self.productfile_set.all()
        return qs


@receiver(pre_save, sender=Product)
def my_callback(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


def upload_file_loc(instance, filename):
    slug = instance.product.slug
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = 'product/{slug}/'.format(slug=instance.product)
    return location + filename


class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(Product, upload_to=upload_file_loc,
                            storage=FileSystemStorage(
                                location=settings.PROTECTED_ROOT))

    def __str__(self):
        return (self.file.name)

    @property
    def name(self):
        return get_filename(self.file.name)

    def get_download_url(self):
        return reverse('products:download', kwargs={"pk":self.pk, "slug":self.product.slug})
