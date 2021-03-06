import random
import string
import os
from django.utils.text import slugify

def get_filename(path):
    return os.path.basename(path)


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    Slug generator based on model fields 'title' and 'slug'
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=randstr
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def unique_key_generator(instance):
    """
    Key generator
    """
    size = random.randint(30, 45)
    key = random_string_generator(size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_order_id_generator(instance)
    return key


def unique_order_id_generator(instance):
    """
    Order id generator
    """
    order_id = random_string_generator(size=10)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=order_id).exists()
    if qs_exists:
        return unique_order_id_generator(instance)
    return order_id
