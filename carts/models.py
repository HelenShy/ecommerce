from django.db import models
from products.models import Product
from django.conf import settings
from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):
    def new_or_get(self, request):
        cart_id = request.session.get('cart_id', None)
        qs = Cart.objects.filter(id=cart_id)
        if qs.count() == 1:
            cart_obj = qs.first()
            if cart_obj.user is None and request.user.is_authenticated:
                cart_obj.user =  request.user
                cart_obj.save( )
            print('Cart already exists')
            new_obj = False
        else:
            print('Create new cart')
            cart_obj = Cart.objects.new(user=request.user)
            request.session['cart_id'] = cart_obj.id
            new_obj = True
        return cart_obj, new_obj

    def new(self, user=None):
        if user is not None:
            if user.is_authenticated:
                return Cart.objects.create(user=user)
        return Cart.objects.create(user=None)


class Cart(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    products = models.ManyToManyField(Product)
    total = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)


def products_changed(sender, instance, action, **kwargs):
    if action == "post_add" or action == "post_remove" or action == "post_clear":
        instance.total = 0
        print(instance)
        products = instance.products.all()
        for product in products:
            instance.total += product.price
        instance.save()


m2m_changed.connect(products_changed, sender=Cart.products.through)

# @receiver(pre_save, sender=Cart)
# def my_callback(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         instance.slug = unique_slug_generator(instance)
