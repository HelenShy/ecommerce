from django.test import TestCase
from accounts.models import User, EmailActivation
from django.urls import reverse

import unittest
from django.utils import timezone
import datetime
from products.models import Product
from tests.test_conf import login, add_products


class TestCartsViews(TestCase):
    def setUp(self):
        add_products()
        login(self.client)

    def test_cart_update_view_redirects(self):
        product_id = Product.objects.all().filter(
            slug='favourite-book').first().id
        resp = self.client.post(reverse('carts:update'),
                                {'product_id':product_id},
                                follow=True)
        self.assertRedirects(
            resp, '/cart/', status_code=302, target_status_code=200, msg_prefix='')

    def test_cart_update_view_contains(self):
        product_id = Product.objects.all().filter(
            slug='favourite-book').first().id
        resp = self.client.post(reverse('carts:update'),
                                {'product_id':product_id},
                                follow=True)
        self.assertContains(resp, "favourite book", status_code=200)

    def test_cart_checkout_contains(self):
        self.client.post(reverse('carts:update'),
                                {'product_id':1},
                                follow=True)
        self.client.post(reverse('carts:update'),
                                {'product_id':2},
                                follow=True)
        resp = self.client.post(reverse('carts:checkout'),
                                follow=True)
        price_1 = Product.objects.filter(id=1).first().price
        price_2 = Product.objects.filter(id=2).first().price
        total = price_1 + price_2
        self.assertContains(resp, total, status_code=200)
