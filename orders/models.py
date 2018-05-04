from django.db import models
from django.db.models.signals import pre_save, post_save

from carts.models import Cart
from billing.models import BillingProfile
from ecommerce.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = {
    ('created', 'Created'),
    ('paid', 'Paid'),
}

class OrderManager(models.Manager):
    def new_or_get(self, billing_obj, cart_obj):
        qs = Order.objects.filter(billing_profile=billing_obj,
                                  cart=cart_obj,
                                  active=True,
                                  status='created')
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = Order.objects.create(billing_profile=billing_obj,
                                       cart=cart_obj)
        created = True
        return obj, created


class Order(models.Model):
    order_id = models.CharField(max_length=40, blank=True)
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default='created', max_length=60)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        self.total = self.cart.total
        self.save()
        return self.total

    def is_prepared(self):
        return self.active and self.billing_profile and self.total > 0

    def set_status_paid(self):
        self.status = 'paid'



def pre_save_create_order_id(sender, instance, *args, **kwargs):
    instance.order_id = unique_order_id_generator(instance)
    old_orders = Order.objects.exclude(
        billing_profile=instance.billing_profile).filter(
            cart=instance.cart,
            active=True)
    if old_orders.exists():
        old_orders.update(active=False)

pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_update_total(sender, instance, created, *args, **kwargs):
    if created:
        print('if created')
        instance.update_total()

post_save.connect(post_save_update_total, sender=Order)


def post_save_update_order(sender, instance, created, *args, **kwargs):
    print('post_save Cart')
    if not created:
        qs = Order.objects.filter(cart__id=instance.id)
        if qs.count() == 1:
            order = qs.first()
            order.update_total()

post_save.connect(post_save_update_order, sender=Cart)
