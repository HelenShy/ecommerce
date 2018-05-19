from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

import unittest
from products.models import Product, ProductFile
from tests.test_conf import login, add_products, add_categories


class TestProductsModels(TestCase):
    def setUp(self):
        add_products()

    def test_upload_files(self):
        product = Product.objects.get(id=1)
        file = ProductFile.objects.create(product=product, file='test.txt')
        downloads = [i.file.name for i in product.get_downloads()]
        self.assertIn(str(file), downloads)
