from django.test import TestCase
from django.urls import reverse

import unittest
from categories.models import Category, Collection


class TestCategoriesModels(TestCase):

    def test_category_str(self):
        category = Category.objects.create(title='Non fiction')
        self.assertEqual(str(category), 'Non fiction')

    def test_category_get_absolute_url(self):
        category = Category.objects.create(title='Non fiction')
        self.assertEqual(category.get_absolute_url(), '/products/category/Non%20fiction/')


    def test_collection_str(self):
        collection = Collection.objects.create(title='Best sellers')
        self.assertEqual(str(collection), 'Best sellers')
