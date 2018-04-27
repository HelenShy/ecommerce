from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

User = setiings.AUTH_USER_MODEL


class BillingProfile(models.Model):
    user = models.OneToOneField(User, blank=True, null=True)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


@receiver(post_save, sender=User)
def my_callback(sender, instance, created, *args, **kwargs):
    if created:
        BillingProfile.objects.get_or_create(user=instance)
