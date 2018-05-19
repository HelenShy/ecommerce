from django.test import TestCase
from django.urls import reverse

import unittest
from products.models import Product
from categories.models import Category, Collection
from tests.test_conf import add_products, add_collections, add_categories


class TestHomeViews(TestCase):
    def setUp(self):
        add_collections()
        add_products()

    def test_home_page_collections(self):
        resp = self.client.get(reverse('home'))
        self.assertContains(resp, "BEST SELLERS",status_code=200)
        self.assertContains(resp, "NON FICTION BOOKS AT BEST PRICES",
                            status_code=200)
        self.assertContains(resp, "MUST READS FOR CHILDREN",
                            status_code=200)

    def test_home_page_collection_products(self):
        product = Product.objects.filter(id=1).first()
        collection = Collection.objects.filter(id=1).first()
        collection.products.add(Product.objects.get(id=1), Product.objects.get(id=2))
        resp = self.client.get('/', follow=True)
        self.assertContains(resp, product.title, status_code=200)


    def test_home_page_genres(self):
        genres = [c.title for c in Category.objects.all()]
        resp = self.client.get(reverse('home'))
        for genre in genres:
            self.assertContains(resp, genre, status_code=200)
