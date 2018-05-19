from django.test import TestCase
from django.urls import reverse

import unittest
from products.models import Product, ProductFile
from categories.models import Category
from tests.test_conf import login, add_products, add_categories


class TestCartsViews(TestCase):
    def setUp(self):
        add_products()
        add_categories()
        login(self.client)

    def test_product_list_view(self):
        product1 = Product.objects.get(id=1)
        product2 = Product.objects.get(id=2)
        resp = self.client.get(reverse('products:list'), follow=True)
        self.assertContains(resp, product1.title, status_code=200)
        self.assertContains(resp, product2.title, status_code=200)

    def test_product_detail_slug_view(self):
        product = Product.objects.filter(id=1).first()
        another_product = Product.objects.filter(id=2).first()
        resp = self.client.get(reverse(
            'products:detail', kwargs={'slug':product.slug}
            ), follow=True)
        self.assertContains(resp, product.title, status_code=200)
        self.assertNotContains(resp, another_product.title, status_code=200)

    def test_products_in_category_view(self):
        product = Product.objects.filter(id=1).first()
        another_product = Product.objects.filter(id=2).first()
        category = Category.objects.filter(id=1).first()
        category.products.add(Product.objects.get(id=1))
        resp = self.client.get(reverse(
            'products:category',
            kwargs={'category':category.title}
            ), follow=True)
        self.assertContains(resp, product.title, status_code=200)
        self.assertNotContains(resp, another_product.title, status_code=200)

    def test_product_download_view_redirect(self):
        product = Product.objects.get(id=1)
        file = ProductFile.objects.create(product=product, file='test.txt')
        downloads = [i.file.name for i in product.get_downloads()]
        resp = self.client.get(reverse('products:download',
                                       kwargs={'slug':product.slug, 'pk':1}
                                       ), follow=True)
        self.assertContains(resp,
                            'You do not have access to download this file.',
                            status_code=200)

    # def test_product_download_view_free_file(self):
    #     product = Product.objects.get(id=1)
    #     file = ProductFile.objects.create(product=product,
    #                                       file='test.txt',
    #                                       free=True)
    #     downloads = [i.file.name for i in product.get_downloads()]
    #     resp = self.client.get(reverse('products:download',
    #                                    kwargs={'slug':product.slug, 'pk':1}
    #                                    ), follow=True)
    #     # print(resp.rendered_content)
    #     #print(dir(resp))
    #     self.assertContains(resp, file, status_code=200)
