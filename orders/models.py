from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.conf import settings
import datetime

from carts.models import Cart
from billing.models import BillingProfile
from products.models import Product
from ecommerce.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = {
    ('created', 'Created'),
    ('paid', 'Paid'),
}

class OrderQuerySet(models.query.QuerySet):
    def by_billing_profile(self, request):
        """
        Returns all orders for the billing profile in request.
        """
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        qs = self.filter(billing_profile=billing_profile)
        return qs

    def not_created(self):
        """
        Returns all orders except the ones with 'created' status.
        """
        return self.exclude(status='created')

    def totals_data(self):
        """
        Returns tuple total and average value of products in order.
        """
        return self.aggregate(total__sum=Coalesce(Sum('total'), 0),
                              total__avg=Coalesce(Avg('total'), 0))

    def totals_cart_data(self):
        """
        Returns tuple total, average value and total quantity of products
        in order.
        """
        return self.aggregate(total__sum=Coalesce(Sum('cart__products__price'), 0),
                              total__avg=Coalesce(Avg('cart__products__price'), 0),
                              total__count=Coalesce(Count('cart__products'), 0))

    def get_sales_breakdown(self):
        """
        Returns detailed statistics about orders.
        """
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
        """
        Returns orders creted in period between start_date and end_date.
        If end_date is None then in period starting from start_date till now.
        """
        if end_date:
            return self.filter(created__gte=start_date).filter(
                created__lte=end_date
            )
        return self.filter(created__gte=start_date)

    def by_week_range(self, qty_weeks_back, qty_weeks=None):
        """
        Returns orders created in selected period defined by weeks.
        :param qty_weeks_back: quantity of weeks ago to return data from.
        :param qty_weeks: quantity of weeks on which data should be returned.
        """
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
        """
        Returns orders created in period of current month.
        """
        now  = timezone.now()
        start_month = datetime.datetime(now.year, now.month, 1)
        return self.by_time_range(start_month)

    def period_totals(self, type, qty_periods_ago):
        """
        Returns totals for orders created starting from defined period of time
        till now.
        :param type: type of period:day, week, month.
        :param qty_periods_ago: quantity of periods (of selected type) data
        should be returned starting from.
        """
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
        """
        Returns all orders.
        """
        return OrderQuerySet(self.model, using=self._db)

    def by_billing_profile(self, request):
        """
        Returns all orders for billing profile in request.
        """
        return self.get_queryset().by_billing_profile(request)

    def new_or_get(self, billing_obj, cart_obj):
        """
        Returns order instance with status 'created' if it already exists or
        creates a new one and returns it.
        """
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
        """
        Updates total sum in order according to cart total.
        """
        self.total = self.cart.total
        self.save()
        return self.total

    def is_prepared(self):
        """
        Returns a boolean value whether order is prepared to be charged.
        """
        return self.active and self.billing_profile and self.total > 0

    def create_purchases(self):
        """
        Adds purchases from the cart to the order instance.
        """
        for p in self.cart.products.all():
            ProductPurchase.objects.get_or_create(
                order_id=self.order_id,
                billing_profile=self.billing_profile,
                product=p
            )
        return ProductPurchase.objects.filter(order_id=self.order_id).count()

    def set_status_paid(self):
        """
        Changes order status to 'paid'.
        """
        if self.status != 'paid':
            if self.is_prepared():
                self.status = 'paid'
                self.save()
                self.create_purchases()
        return self.status

    def get_absolute_url(self):
        """
        Returns url for the order.
        """
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
        instance.update_total()

post_save.connect(post_save_update_total, sender=Order)


def post_save_update_order(sender, instance, created, *args, **kwargs):
    if not created:
        qs = Order.objects.filter(cart__id=instance.id)
        if qs.count() == 1:
            order = qs.first()
            order.update_total()

post_save.connect(post_save_update_order, sender=Cart)


class ProductPurchaseQuerySet(models.query.QuerySet):
    def by_billing_profile(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        qs = self.filter(billing_profile=billing_profile)
        return qs


class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def by_billing_profile(self, request):
        return self.get_queryset().by_billing_profile(request)

    def products_by_request(self, request):
        qs = self.by_billing_profile(request)
        product_ids = [x.product.id for x in qs]
        products = Product.objects.filter(id__in=product_ids).distinct()
        return products

    def last_order(self, request):
        last_order = Order.objects.by_billing_profile(
            request).order_by('-created').first()
        queryset = self.get_queryset().filter(order_id=last_order.order_id).all()
        product_ids = [x.product.id for x in queryset]
        products = Product.objects.filter(id__in=product_ids).distinct()
        return products

    def purchased(self, request):
        qs_purchased = self.products_by_request(request)
        return  qs_purchased


class ProductPurchase(models.Model):
    order_id = models.CharField(max_length=40)
    billing_profile = models.ForeignKey(BillingProfile,
                                        on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title
