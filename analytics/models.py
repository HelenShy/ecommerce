from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import BaseUserManager

from .signals import object_viewed_signal
from .utils import get_user_ip

User = settings.AUTH_USER_MODEL


class ObjectViewedQuerySet(models.query.QuerySet):
    def by_model(self, models_class, distinct=True):
        """
        Returns all viewed objects of model type passed as 'models_class'
        argument.
        """
        c_type = ContentType.objects.get_for_model(models_class)
        qs = self.filter(content_type=c_type)
        if distinct:
            qs_ids = [x.object_id for x in qs]
            qs = models_class.objects.filter(pk__in=qs_ids)
        return qs


class ObjectViewedManager(BaseUserManager):
    def get_queryset(self):
        """
        Returns all viewed objects of model type passed as 'models_class'
        argument.
        """
        return ObjectViewedQuerySet(self.model, using=self._db)

    def by_model(self, models_class, distinct=True):
        """
        Returns distinct viewed objects of model type passed as 'models_class'
        argument.
        """
        qs = ObjectViewedQuerySet(self.model, using=self._db)
        return qs.by_model(models_class, distinct)


class ObjectViewed(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=220,  blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(auto_now_add=True)

    objects = ObjectViewedManager()

    def __str__(self):
        return "%s viewed %s".format(self.content_object, self.created)

    class Meta:
        ordering =['-created']
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'


def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    obj_cls = ContentType.objects.get_for_model(sender)
    if request.user.is_authenticated:
        user_requested = request.user
    else:
        user_requested = None
    new_view_obj = ObjectViewed.objects.create(
        user = user_requested,
        ip_address = get_user_ip(request),
        content_type = obj_cls,
        object_id = instance.id
    )


object_viewed_signal.connect(object_viewed_receiver)
