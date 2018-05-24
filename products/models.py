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
from ecommerce.aws.utils import ProtectedS3BototStorage
from ecommerce.aws.download.utils import AWSDownload


def get_filename_ext(filepath):
    """
    Extracts file name and extension.
    """
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    """
    Returns image path.
    """
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


class ProductQuerySet(models.query.QuerySet):
    def by_category(self, category):
        """
        Returns all products for defined category.
        """
        products = Product.objects.all()
        qs = self.filter(Q(category__title=category))
        return qs

    def by_collection(self, collection):
        """
        Returns all products for defined collection.
        """
        products = Product.objects.all()
        qs = self.filter(Q(collection__title=collection))
        return qs

    def by_author(self, author):
        """
        Returns all products for defined author.
        """
        products = Product.objects.all()
        qs = self.filter(Q(author__name=author))
        return qs


class ProductManager(models.Manager):
    def get_queryset(self):
        """
        Returns all products.
        """
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        """
        Returns all active products.
        """
        return self.get_queryset().filter(active=True)

    def search(self, query):
        """
        Returns products filtering by title, description, category, author name.
        """
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(category__title__icontains=query) |
                   Q(author__name__icontains=query))
        return self.get_queryset().filter(lookups).distinct()

    def by_category(self, category):
        """
        Returns all active products for defined category.
        """
        return self.all().by_category(category)

    def by_collection(self, collection):
        """
        Returns all active products for defined collection.
        """
        return self.all().by_collection(collection)

    def by_author(self, author):
        """
        Returns all active products for defined author.
        """
        return self.all().by_author(author)


class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    image = models.ImageField(upload_to=upload_image_path,
                              null=True,
                              blank=True)
    active = models.BooleanField(default=True)

    objects = ProductManager()
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Returns product`s url.
        """
        return reverse("products:detail", kwargs={'slug': self.slug})

    @property
    def name(self):
        return self.title

    @property
    def authors(self):
        authors = ", ".join([author.name for author in self.author_set.all()])
        return authors

    def get_downloads(self):
        """
        Returns list of files that are attached to the product and can be
        downloaded.
        """
        qs = self.productfile_set.all()
        return qs


@receiver(pre_save, sender=Product)
def my_callback(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


def upload_file_loc(instance, filename):
    """
    Returns path to which uploaded product can be uploaded.
    """
    slug = instance.product.slug
    _id = instance.id
    if _id is None:
        Klass = instance.__class__
        qs = Klass.objects.all().order_by('-pk')
        if qs.exists():
            _id = qs.first() + 1
        else:
            _id = 0
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = 'product/{slug}/{id}'.format(slug=instance.product, id=_id)
    return location + filename


class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=True, blank=True)
    file = models.FileField(Product, upload_to=upload_file_loc,
                            storage=ProtectedS3BototStorage())
    free = models.BooleanField(default=False)

    def __str__(self):
        return (self.file.name)

    @property
    def display_name(self):
        orig_name = get_filename(self.file.name)
        if self.name:
            return self.name
        return orig_name

    def get_default_url(self):
        """
        Returns url of the product.
        """
        return self.product.get_absolute_url()

    def generate_download_url(self):
        """
        Generates download url for the file.
        """ 
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        if not bucket or region or access_key or secret_key:
            return "/"
        PROTECTED_DIR_NAME = getattr(settings, 
                                    'PROTECTED_DIR_NAME', 
                                    'protected')
        path = "{base}/{file_path}".format(base=PROTECTED_DIR_NAME,
                                            file_path=str(self.file))
        aws_dl_object = AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path, new_filename=self.display_name)
        return file_url

    def get_download_url(self):
        """
        Returns url to download product from.
        """
        return reverse('products:download', kwargs={"pk":self.pk,
                                                    "slug":self.product.slug})
