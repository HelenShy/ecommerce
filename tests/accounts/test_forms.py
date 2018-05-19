from django.test import TestCase
# Create your tests here.
import unittest
from django.urls import reverse
from accounts.forms import RegisterForm, LoginForm
from accounts.models import User, EmailActivation


class TestAccountsForms(TestCase):

    def test_register_form(self):
        email = 'tes@mail.com'
        password = '1j3m4mm3'

        data = {'name':'test', 'email':email, 'password1':password, 'password2':password}
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
