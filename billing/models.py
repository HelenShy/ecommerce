from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from accounts.models import GuestUser

User = settings.AUTH_USER_MODEL


class BillingManager(models.Manager):
    def new_or_get(self, request):
        user = request.user
        guest_id = request.session.get('guest_id')
        obj = None
        created = False
        if user.is_authenticated:
            obj,created = BillingProfile.objects.get_or_create(
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
    objects = BillingManager()

    def __str__(self):
        return self.email


@receiver(post_save, sender=User)
def my_callback(sender, instance, created, *args, **kwargs):
    if created:
        BillingProfile.objects.get_or_create(user=instance)
