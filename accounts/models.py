from django.db import models
from django.db.models import Q
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager)
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import get_template
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from datetime import timedelta

from ecommerce.utils import unique_key_generator


class UserManager(BaseUserManager):
    """
    Helps Django to work with our custom user model.
    """
    def create_user(self, email, password, name=None):
        """
        Creates a new user profile object
        """
        if not email:
            raise ValueError('User must have email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_staffuser(self, email, password, name=None):
        """
        Creates a new superuser profile object
        """
        user = self.create_user(email=email, password=password, name=name)
        user.staff = True

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, name=None):
        """
        Creates a new superuser profile object
        """
        user = self.create_user(email=email, password=password, name=name)
        user.is_superuser = True
        user.staff = True
        user.admin = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def get_full_name(self):
        """
        Used to get a users full name
        """
        return self.name

    def get_short_name(self):
        """
        Used to get a users short name
        """
        return self.name

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        if self.is_admin:
            return True
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class EmailActivationQuerySet(models.query.QuerySet):
    def confirmable(self):
        now = timezone.now()
        start_date = now - timedelta(days=settings.DEFAULT_ACTIVATION_DAYS)
        return self.filter(activated=False, forced_expired=False).exclude(
            created__lt=start_date
        )


class EmailActivationManager(BaseUserManager):
    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        qs = self.get_queryset().filter(
            Q(email=email) | Q(user__email=email)).filter(activated=False)
        return  qs


class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, unique=True)
    key = models.CharField(max_length=120, blank=True, null=True)
    activated = models.BooleanField(default=False)
    forced_expired = models.BooleanField(default=False)
    expires = models.IntegerField(default=7)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        return qs.exists()

    def activate(self):
        if self.can_activate():
            user = self.user
            user.is_active = True
            user.save()
            self.activated = True
            self.save()
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expired:
            if self.key:
                base_url = getattr(settings, 'BASE_URL')
                key_path = reverse('account:email-activate', kwargs={'key': self.key})
                path = "{base}{path}".format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template('registration/emails/verify.txt').render(context)
                html_ = get_template('registration/emails/verify.html').render(context)
                subject = 'Email verification'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipients_list = [self.email]
                sent_mail = send_mail(
                    subject,
                    txt_,
                    from_email,
                    recipients_list,
                    html_message=html_,
                    fail_silently=False
                )
                return sent_mail
        return False

    def regenerate_key(self):
        self.key = None
        sself.save()
        return self.key is not None

    def create_activation_key(self):
        key = unique_key_generator()
        qs = EmailActivation.objects.filter(key=key)
        if qs.exists():
            create_activation_key()
        return key


def post_save_send_email_activation(sender, instance, created, *args, **kwargs):
    if created:
        obj = EmailActivation.objects.create(user=instance, email=instance.email)
        obj.send_activation()

post_save.connect(post_save_send_email_activation, sender=User)


def pre_save_email_activation(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expired:
        if not instance.key:
            instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation, sender=EmailActivation)


class GuestUser(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
