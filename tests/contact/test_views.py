from django.test import TestCase
# Create your tests here.
import unittest
from django.urls import reverse
from contact.forms import ContactForm


class TestContactViews(TestCase):

    def test_contact_view_redirects(self):
        name = 'test'
        email = 'test@mail.com'
        message = 'Hello'

        data = {'name':name, 'email':email, 'message':message}
        resp = self.client.post(reverse('contact'), data, follow=True)
        self.assertRedirects(resp, '/', status_code=302,
                             target_status_code=200, msg_prefix='')


    def test_contact_view_contains(self):
        name = 'test'
        email = 'test@mail.com'
        message = 'Hello'

        data = {'name':name, 'email':email, 'message':message}
        resp = self.client.post(reverse('contact'), data, follow=True)
        self.assertContains(resp,
                            'Thank you for your inquiry.',
                            status_code=200)
