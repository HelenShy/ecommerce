from django.test import TestCase
from django.urls import reverse

import unittest
from products.models import Product
from tests.test_conf import add_products


class TestCartsViews(TestCase):
    def setUp(self):
        add_products()

    def test_search_product_view(self):
        product1_title = Product.objects.filter(id=1).first().title
        product2_title = Product.objects.filter(id=2).first().title
        resp = self.client.get(
            reverse('search:query'),
            {'q': product1_title},
            follow=True)
        self.assertContains(resp, product1_title, status_code=200)
        self.assertNotContains(resp, product2_title, status_code=200)
        resp = self.client.get(
            reverse('search:query'),
            {'q': product2_title},
            follow=True)
        self.assertContains(resp, product2_title, status_code=200)
        self.assertNotContains(resp, product1_title, status_code=200)
