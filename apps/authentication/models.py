import datetime

import hashlib
import re
from apps.administration.utils import mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from apps.user.models import User
from MTShowcase import settings

SHA1_RE = re.compile('^[a-f0-9]{40}$')


# VALIDATORS
def validate_haw_mail(value):
    if not value.endswith('@haw-hamburg.de'):
        raise ValidationError(message="{} endet nicht mit '@haw-hamburg.de".format(value))


name_validator = RegexValidator(
    regex='^[a-zA-Züöäß]{1,100}$',
    message=_('Namen dürfen nur aus Buchstaben bestehen.').format(),
    code='invalid_firstname'
)


class AuthEmailUserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
         Create a new user using email and password and
         return the new user.
        """
        if settings.AUTH_DEBUG:
            print("#--#--------" + "CREATE NEW USER" + "--------#--#")
        if not email:
            raise ValueError("The given email must be set")

        now = timezone.now()
        email = self.normalize_email(email)
        is_active = extra_fields.pop("is_active", True)
        user = self.model(email=email,
                          is_active=is_active,  # set user to inactive until he confirms his email
                          is_superuser=is_superuser,
                          is_staff=is_staff,
                          last_login=now,
                          )
        user.set_password(password)
        user.save(self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        is_staff = extra_fields.pop("is_staff", False)
        return self._create_user(email, password, is_staff=is_staff, is_superuser=False, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        return self._create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)


class AuthEmailUser(AbstractBaseUser, PermissionsMixin):
    """
    Inherited fields :
        password
        last_login

        is_superuser: able to login into django admin page?
        groups
        user_permissions

    """
    email = models.EmailField(unique=True, validators=[validate_haw_mail], verbose_name='email address', db_index=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100, blank=True,
                                  validators=[name_validator])  # blank = allowing empty value in form
    last_name = models.CharField(max_length=100, blank=True,
                                 validators=[name_validator])  # can include middle names with blank space in between

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # make Django use email instead of username to login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AuthEmailUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return serializers.serialize('json', [self, ])

    def get_short_name(self):
        """Return the email."""
        return self.email

    def get_full_name(self):
        """Return the email."""
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        if settings.AUTH_DEBUG:
            print("#--#--------" + "ACTIVATION MAIL SEND" + "--------#--#")
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_lib_user(self):
        return User.objects.filter(auth_user=self).get()


class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "ACTIONVATION START" + "--------#--#")
        # check if valid sha1 hash
        if SHA1_RE.search(activation_key.lower()):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()

                if settings.AUTH_DEBUG:
                    print("#--#--------" + "CREATE SHOWCASE USER" + "--------#--#")
                # create showcase user
                new_user = User(alias=user.first_name.capitalize())
                new_user.auth_user = user
                # because first and last name are set from email
                # the combination must be unique
                new_user.unique_name = user.first_name + user.last_name
                new_user.save()

                return new_user
        return False

    def create_inactive_user(self, form):
        """
        Create inactive user and email confirmation key
        """
        if settings.AUTH_DEBUG:
            print("#--#--------" + "CREATE INACTIVE USER" + "--------#--#")
        new_user = form.save(commit=False)
        new_user.is_active = False
        self.set_first_last_name(new_user, form.cleaned_data['email'])
        new_user.save()

        registration_profile = self.create_profile(new_user)
        registration_profile.send_activation_email()

        return new_user

    def create_profile(self, user):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "GENERATE KEY" + "--------#--#")
            print("#--#--------" + "ABOUT TO CREATE USER" + "--------#--#")

        User = AuthEmailUser
        email = str(getattr(user, User.USERNAME_FIELD))
        hash_input = (get_random_string(5) + email).encode('utf-8')
        activation_key = hashlib.sha1(hash_input).hexdigest()
        key_expires = timezone.now() + timezone.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        print("user activation key endet in :")
        print(key_expires)

        return self.create(user=user, activation_key=activation_key, key_expires=key_expires)

    def set_first_last_name(self, user, data):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "SET USER NAMES" + "--------#--#")
        email = user.email
        names = (str(email).split("@")[0]).split(".")
        user.first_name = names[0].capitalize()
        user.last_name = names[1].capitalize()

    def expired(self):
        """
        Query for all profiles whose activation key has expired.
        """
        if settings.AUTH_DEBUG:
            print("#--#--------" + "CHECK PROFILE KEYEXPIRE" + "--------#--#")
        now = datetime.datetime.now()
        return self.filter(
            models.Q(activation_key=self.model.ACTIVATED) |
            models.Q(
                key_expires__lt=now - datetime.timedelta(
                    settings.ACCOUNT_ACTIVATION_DAYS
                )
            )
        )

    def delete_expired_users(self):
        for profile in self.expired():
            user = profile.user
            profile.delete()
            user.delete()


class RegistrationProfile(models.Model):
    ACTIVATED = "ALREADY_ACTIVATED"

    user = models.OneToOneField('authentication.AuthEmailUser', on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    objects = RegistrationManager()

    def activation_key_expired(self):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "CHECK KEY EXPIRE" + "--------#--#")
        return self.activation_key == self.ACTIVATED or \
               (self.key_expires <= timezone.now())

    def send_activation_email(self):
        if settings.AUTH_DEBUG:
            print("#--#--------" + "ABOUT TO SEND ACTIVATION MAIL" + "--------#--#")
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'user': self.user,
                    'site': settings.SITE,
                    'domain': settings.DOMAIN}

        rendered = mail('authentication/activation_email_subject.txt',
                        'authentication/activation_email.txt',
                        ctx_dict, commit=False)
        self.user.email_user(*rendered, from_email=settings.DEFAULT_FROM_EMAIL)
