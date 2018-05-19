from django.test import TestCase
# Create your tests here.
import unittest
from django.urls import reverse
from contact.forms import ContactForm


class TestContactForms(TestCase):

    def test_contact_form(self):
        name = 'test'
        email = 'tes@mail.com'
        message = 'Hello'

        data = {'name':name, 'email':email, 'message':message}
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
