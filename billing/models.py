from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from django.conf import settings
from accounts.models import GuestUser
import stripe

User = settings.AUTH_USER_MODEL
stripe.api_key = settings.STRIPE_SECRET_KEY


class BillingManager(models.Manager):
    def new_or_get(self, request):
        """
        Returns existing or creates new billing object for current user.
        """
        user = request.user
        guest_id = request.session.get('guest_id')
        print(guest_id)
        obj = None
        created = False
        if user.is_authenticated:
            obj, created = BillingProfile.objects.get_or_create(
                user=user, email=user.email)
        elif guest_id is not None:
            guest = GuestUser.objects.get(id=guest_id)
            obj, created = BillingProfile.objects.get_or_create(
                email=guest.email)
        return obj, created


class BillingProfile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    stripe_id = models.CharField(max_length=120, blank=True, null=True)
    objects = BillingManager()

    def __str__(self):
        return self.email

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    def get_cards(self):
        """
        Returns cards saved by current user.
        """
        return self.card_set.all()

    @property
    def has_card(self):
        """
        Returns True if there are saved cards for current user or False if not.
        """
        return self.get_cards().exists()

    @property
    def default_card(self):
        """
        Returns default card number for current user profile if there is one.
        Else None.
        """
        qs = self.get_cards().filter(default=True, active=True)
        if qs.exists():
            return qs.first()
        return None

    def set_cards_inactive(self):
        """
        Deactivates cards for the user.
        """
        cards = self.get_cards()
        cards.update(active=False)
        return cards.filter(active=True).count()

    def get_payment_method(self):
        """
        Returns reference  to 'billing:payment' page.
        """
        return reverse('billing:payment')



def pre_save_create_stripe_id(sender, instance, *args, **kwargs):
    print("instance.stripe_id")
    print(instance.stripe_id)
    if not instance.stripe_id:
        stripe_customer = stripe.Customer.create(email=instance.email)
        instance.stripe_id = stripe_customer.id

pre_save.connect(pre_save_create_stripe_id, sender=BillingProfile)


def post_save_create_billing_profile(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(post_save_create_billing_profile, sender=User)


class CardManager(models.Manager):
    def add_new(self, billing_profile, card_response):
        """
        Adds new card to billing profile.
        """
        if str(card_response.object) == "card":
            new_card = self.model(
                billing_profile=billing_profile,
                stripe_id=card_response.stripe_id,
                brand=card_response.brand,
                country=card_response.country,
                exp_month=card_response.exp_month,
                exp_year=card_response.exp_year,
                last4=card_response.last4,
            )
            new_card.save()
            return new_card
        return None

    def all(self, *args, **kwargs):
        """
        Returns all active cards.
        """
        return self.get_queryset().filter(active=True)


class Card(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120)
    brand = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    exp_month = models.IntegerField()
    exp_year = models.IntegerField()
    last4 =  models.CharField(max_length=4, blank=True, null=True)
    default =  models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return "{0} {1}".format(self.brand, self.last4)


def post_save_change_default(sender, instance, created, *args, **kwargs):
    if instance.default:
        print(instance.default)
        print("instance.default")
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)

post_save.connect(post_save_change_default, sender=Card)


class ChargeManager(models.Manager):
    def do(self, billing_profile, order_obj, card=None):
        """
        Charges for the purchase on site.
        """
        card_obj = card
        if card is None:
            cards = billing_profile.card_set.filter(default=True)
            if cards.exists():
                card_obj = cards.first()
            else:
                return False, "No cards available"
        charge_response = stripe.Charge.create(
            amount=int(order_obj.total * 100),
            currency="usd",
            customer=billing_profile.stripe_id,
            source=card_obj.stripe_id,
            description="Charge for BookShop@gmail.com"
        )
        charge_obj = self.model(
            billing_profile=billing_profile,
            stripe_id=charge_response.stripe_id,
            paid=charge_response.paid,
            refunded=charge_response.refunded,
            outcome=charge_response.outcome,
            outcome_type=charge_response.outcome['type'],
            seller_message=charge_response.outcome.get('seller_message'),
            risk_level=charge_response.outcome.get('risk_level'),
        )
        charge_obj.save()
        return charge_obj.paid, charge_obj.seller_message


class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id =  models.CharField(max_length=120)
    paid =  models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)
    outcome_type = models.CharField(max_length=120, null=True, blank=True)
    seller_message = models.CharField(max_length=120, null=True, blank=True)
    risk_level = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()

    def __str__(self):
        return "{}".format(self.stripe_id)
