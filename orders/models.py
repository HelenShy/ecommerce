from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from carts.models import Cart
from ecommerce.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = {
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('pending', 'Pending'),
}

class Order(models.Model):
    order_id = models.CharField(max_length=40, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, default='created', max_length=60)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_id

    def update_total(self):
        print("self.cart.total")
        print(self.cart.total)
        self.total = self.cart.total
        print("self.total")
        print(self.total)
        self.save()
        return self.total


@receiver(pre_save, sender=Order)
def my_callback(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)

@receiver(post_save, sender=Order)
def my_callback(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

@receiver(post_save, sender=Cart)
def my_callback(sender, instance, created, *args, **kwargs):
    if not created:
        qs = Order.objects.filter(cart__id=instance.id)
        if qs.count() == 1:
            order = qs.first()
            order.update_total()
