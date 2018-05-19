from accounts.models import User, EmailActivation
from django.urls import reverse

from products.models import Product
from categories.models import Category, Collection


def login(client):
    email = 'test@mail.com'
    password = '1j3m4mm3'
    data = {'name':'test',
            'email':email,
            'password1':password,
            'password2':password}
    client.post(reverse('register'), data, follow=True)
    user = User.objects.filter(email=email).first()
    email_activation = EmailActivation.objects.filter(
        email=email).first()
    user.is_active = True
    user.save()
    email_activation.activated = True
    email_activation.save()
    data = {'email':email, 'password':password}
    client.post(reverse('login'), data, follow=True)


def login_as_admin(client):
    email = 'test@mail.com'
    password = '1j3m4mm3'
    data = {'name':'test',
            'email':email,
            'password1':password,
            'password2':password}
    client.post(reverse('register'), data, follow=True)
    user = User.objects.filter(email=email).first()
    email_activation = EmailActivation.objects.filter(
        email=email).first()
    user.is_active = True
    user.staff = True
    user.admin = True
    user.save()
    email_activation.activated = True
    email_activation.save()
    data = {'email':email, 'password':password}
    client.post(reverse('login'), data, follow=True)


def add_products():
    data = [{'title':'favourite book',
             'description':'Read it',
             'image':'products/3550967918/3550967918.jpg',
             'price':100},
            {'title':'War and Peace',
             'description':'By Leo Tolstoy',
             'image':'products/3550967918/3550967918.jpg',
             'price':300},
            ]
    for product_data in data:
        product = Product.objects.create(**product_data)
        product.save()


def add_categories():
    data = ['Non fiction', 'Business', 'Fantasy']
    for i in data:
        cat = Category.objects.create(title=i)


def add_collections():
    data = [{'title':'Bestseller'},
            {'title':'Children'},
            {'title':'Non fiction'}]
    for coll_data in data:
        collection = Collection.objects.create(**coll_data)
        collection.save()
