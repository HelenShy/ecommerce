from django.test import TestCase
from accounts.models import User, EmailActivation
from django.urls import reverse

import unittest
from django.utils import timezone
import datetime
from products.models import Product
from tests.test_conf import login_as_admin, add_products


class TestAnalyticsViews(TestCase):
    def setUp(self):
        login_as_admin(self.client)
        add_products()

    def test_products_history_view(self):
        slug = Product.objects.filter(id=1).first().slug
        self.client.get(reverse('products:detail', kwargs={'slug':slug}), follow=True)
        resp =  self.client.get(reverse('products_history'), follow=True)
        self.assertContains(resp, "favourite book", status_code=200)

    def test_sales_view(self):
        resp =  self.client.get(reverse('sales_analytics'), follow=True)
        self.assertContains(resp, "Today sales data", status_code=200)
