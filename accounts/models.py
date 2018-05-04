from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager)
from django.core.mail import send_mail
from django.template.loader import get_template


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
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class GuestUser(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
