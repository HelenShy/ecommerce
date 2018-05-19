from django.test import TestCase
from accounts.models import User, EmailActivation
from django.urls import reverse

import unittest
from django.utils import timezone
import datetime



class TestAccountsViews(TestCase):

    def setUp(self):
        self.client.force_login(User.objects.get_or_create(
            email='testuser@mail.com', password='1234g5678a')[0])

    def test_home_page(self):
        resp =  self.client.get(reverse('home'), follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_register_page_redirects(self):
        email = 'test1@mail.com'
        password = '1j3m4mm3'
        data = {'name':'test',
                'email':email,
                'password1':password,
                'password2':password}
        resp = self.client.post(reverse('register'), data, follow=True)
        self.assertRedirects(
            resp,
            '/login/',
            status_code=302,
            target_status_code=200,
            msg_prefix='')

    def test_register_page_msg(self):
        email = 'test2@mail.com'
        password = '1j3m4mm3'
        data = {'name':'test',
                'email':email,
                'password1':password,
                'password2':password}
        resp = self.client.post(reverse('register'), data, follow=True)
        self.assertContains(
            resp, "Please check your email and confirm your account.",
            status_code=200)

    def test_login_page_redirects(self):
        email = 'test3@mail.com'
        password = '1j3m4mm3'
        data = {'name':'test',
                'email':email,
                'password1':password,
                'password2':password}
        self.client.post(reverse('register'), data, follow=True)
        user = User.objects.filter(
            email=email).first()
        email_activation = EmailActivation.objects.filter(
            email=email).first()
        user.is_active = True
        user.save()
        email_activation.activated = True
        email_activation.save()

        data = {'email':email, 'password':password}
        resp = self.client.post(reverse('login'), data, follow=True)
        self.assertRedirects(
            resp, '/', status_code=302, target_status_code=200, msg_prefix='')

    def test_login_page_msg1(self):
        email = 'test4@mail.com'
        password = '1j3m4mm3'
        data = {'name':'test',
                'email':email,
                'password1':password,
                'password2':password}
        self.client.post(reverse('register'), data, follow=True)

        data = {'email':email, 'password':password}
        resp = self.client.post(reverse('login'), data, follow=True)
        self.assertContains(
            resp, "Check your mail for confirmation letter.",
            status_code=200)

        def test_login_page_msg2(self):
            email = 'test5@mail.com'
            password = '1j3m4mm3'
            data = {'name':'test',
                    'email':email,
                    'password1':password,
                    'password2':password}
            self.client.post(reverse('register'), data, follow=True)
            email_activation = EmailActivation.objects.filter(
                email=email).first()
            now  = timezone.now()
            email_activation.created = now -  datetime.timedelta(days=10)

            data = {'email':email, 'password':password}
            resp = self.client.post(reverse('login'), data, follow=True)
            self.assertContains(
                resp, "Mail is not confirmed.",
                status_code=200)
