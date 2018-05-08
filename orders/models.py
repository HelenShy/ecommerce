from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from django.db.models.functions import Coalesce
import datetime

from carts.models import Cart
from billing.models import BillingProfile
from ecommerce.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = {
    ('created', 'Created'),
    ('paid', 'Paid'),
}

class OrderQuerySet(models.query.QuerySet):
    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        qs = self.filter(billing_profile=billing_profile)
        return qs

    def not_created(self):
        return self.exclude(status='created')

    def totals_data(self):
        return self.aggregate(total__sum=Coalesce(Sum('total'), 0),
                              total__avg=Coalesce(Avg('total'), 0))

    def totals_cart_data(self):
        return self.aggregate(total__sum=Coalesce(Sum('cart__products__price'), 0),
                              total__avg=Coalesce(Avg('cart__products__price'), 0),
                              total__count=Coalesce(Count('cart__products'), 0))

    def get_sales_breakdown(self):
        recent_orders = self.all()
        recent_orders_totals = recent_orders.totals_data()
        recent_orders_cart_data = recent_orders.totals_cart_data()
        recent_paid_orders = recent_orders.filter(status='paid')
        recent_paid_orders_totals = recent_orders.filter(
            status='paid').totals_data()
        data = {
            'recent_orders': recent_orders,
            'recent_orders_totals': recent_orders_totals,
            'recent_orders_cart_data': recent_orders_cart_data,
            'recent_paid_orders': recent_paid_orders,
            'recent_paid_orders_totals': recent_paid_orders_totals
            }
        return data

    def by_time_range(self, start_date, end_date=None):
        if end_date:
            return self.filter(created__gte=start_date).filter(
                created__lte=end_date
            )
        return self.filter(created__gte=start_date)

    def by_week_range(self, qty_weeks_back, qty_weeks=None):
        now  = timezone.now()
        start_date_days = qty_weeks_back * 7
        start_date = now -  datetime.timedelta(
            days=start_date_days)
        if not qty_weeks:
            return self.by_time_range(start_date)
        end_date_days = qty_weeks * 7
        end_date = now - datetime.timedelta(
            days=end_date_days)
        return self.by_time_range(start_date, end_date)

    def by_month(self):
        now  = timezone.now()
        start_month = datetime.datetime(now.year, now.month, 1)
        return self.by_time_range(start_month)

    def period_totals(self, type, qty_periods_ago):
        labels = []
        totals = []
        days_coef_dict = {
            'day': 1,
            'week': 7,
            'month': 30}
        days_coef = days_coef_dict.get(type, 1)
        start_date = timezone.now() - datetime.timedelta(
            days=days_coef * (qty_periods_ago -1))
        for period in range(0, qty_periods_ago):
            new_date = start_date + datetime.timedelta(days=period*days_coef)
            if  type == 'day':
                labels.append(new_date.strftime("%a"))
            else:
                labels.append(new_date.strftime("%d %b"))
            qs = self.by_time_range(new_date, new_date + datetime.timedelta(days_coef))
            period_totals = qs.get_sales_breakdown()['recent_paid_orders_totals']['total__sum']
            totals.append(period_totals)
        return labels, totals



class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def by_billing_profile(self, request):
        return self.get_queryset().by_billing_profile(request)

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

    class Meta:
        ordering = ['-created', '-changed']

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
        self.save()

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})



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
