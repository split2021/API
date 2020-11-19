from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.core.files.base import File
from django.db.models.query import QuerySet
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.postgres import fields as postgres

import json
from enum import IntEnum, unique

from django_modelapiview import JSONMixin

# Create your models here.

class UserQuerySet(models.QuerySet):
    """
    Add password hashing on update
    """

    def update(self, *args, **kwargs):
        if 'password' in kwargs:
            kwargs['password'] = make_password(kwargs['password'])
        return super().update(*args, **kwargs)


class UserManager(BaseUserManager):
    """
    Define a model manager for User model with no username field
    """

    use_in_migrations = True

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a regular User with the given email and password
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    create = create_user


def get_icon_path(instance, filename):
    return f"{instance.email}/{filename}"
class User(AbstractUser, JSONMixin):
    """
    User model
    """

    email = models.EmailField('email address', unique=True)
    phone = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=20, blank=True)
    friends = models.ManyToManyField("self", blank=True, through="Friendship", through_fields=('user1', 'user2'), related_name="users", symmetrical=False) # To moddify https://www.caktusgroup.com/blog/2009/08/14/creating-recursive-symmetrical-many-to-many-relationships-in-django/
    payment_methods = models.ManyToManyField("PaymentMethod", blank=True, related_name="users")
    score = models.IntegerField(default=0)
    title = models.CharField(max_length=255)
    icon = models.ImageField(upload_to=get_icon_path, default="split.png")
    pro = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    json_fields = ['email', 'last_name', 'first_name', 'phone', 'username', 'friends', 'payment_methods', 'payment_groups', 'friends_count', 'payment_methods_count', 'icon', 'pro']

    objects = UserManager()

    def friends_count(self):
        return self.friends.count()

    def payment_methods_count(self):
        return self.payment_methods.count()

    @staticmethod
    def add_default_permissions(sender, **kwargs):
        print("User post saved")
        user = kwargs['instance']
        if kwargs['created']:
            user.groups.add(Group.objects.get_or_create(name="Client")[0].id)

    def save(self, *args, **kwargs):
        try:
            this = User.objects.get(id=self.id)
            if this.icon != self.icon:
                this.icon.delete(save=False)
        except: pass
        super().save(*args, **kwargs)


class Friendship(models.Model, JSONMixin):
    user1 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user2")

    json_fields = ['user1', 'user2']

    class Meta:
        unique_together = ('user1', 'user2')


class PaymentMethod(models.Model):
    """
    A generic class which is derived in specific payment methods
    """

    name = models.CharField(max_length=42)

    json_fields = ['name', 'users']

    class Meta:
        pass


class PaymentGroupMembership(models.Model, JSONMixin):
    group = models.ForeignKey("PaymentGroup", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    json_fields = ['group', 'user']

    class Meta:
        unique_together = ('group', 'user')


class PaymentGroup(models.Model, JSONMixin):
    """
    Store a list of users than can make payments together
    """

    name = models.CharField(max_length=42)
    users = models.ManyToManyField("User", blank=True, through="PaymentGroupMembership", through_fields=('group', 'user'), related_name="payment_groups")

    json_fields = ['name', 'users']

    def __str__(self):
        return self.name

    class Meta:
        pass


class LogManager(models.Manager):
    """
    """
    def create(self, **kwargs):
        if kwargs['post']:
            if 'password' in kwargs['post']:
                kwargs['post']['password'] = "**********"
        if 'Content-Type' in kwargs['headers'] and kwargs['headers']['Content-Type'] == "application/json":
            try:
                json_body = json.loads(kwargs['body'].decode())
            except:
                pass
            else:
                if 'password' in json_body:
                    json_body['password'] = "**********"
                kwargs['body'] = json.dumps(json_body)
        return super().create(**kwargs)

class Log(models.Model):
    """
    Store requests made against the API for easier debugging
    """
    METHODS = ('HEAD', 'OPTIONS', 'GET', 'PATCH', 'POST', 'PUT', 'DELETE')

    date = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=100)
    method = models.CharField(max_length=10)
    headers = postgres.JSONField()
    body = models.TextField(default="")
    get = postgres.JSONField()
    post = postgres.JSONField()

    objects = LogManager()


class Payment(models.Model, JSONMixin):
    """
    """

    OUR_FEE = 1.042
    OUR_FLAT = 0.45
    OUR_FEE_INVERSED = 1/OUR_FEE
    PAYMENT_FEE = 1.041
    PAYOUT_FLAT = 0.35
    CHECKOUT_FLAT = 0.35
    PAYMENT_FEE_INVERSED = 1/PAYMENT_FEE

    EURO = "EUR"
    USD = "USD"

    CURRENCIES = [
        (EURO, "Euro"),
        (USD, "USD"),
    ]

    payments = postgres.JSONField(default=dict, blank=True)
    group = models.ForeignKey("PaymentGroup", related_name="payments", on_delete=models.SET_NULL, null=True)
    total = models.FloatField()
    currency = models.CharField(max_length=4, choices=CURRENCIES, default=EURO)
    target = models.EmailField()

    json_fields = ['payments', 'group', 'total', 'currency']

    @unique
    class STATUS(IntEnum):
        """
        """

        COMPLETED = 0
        FAILED = 1
        PROCESSING = 2
        REFUNDED = 3

    def is_complete(self):
        for infos in self.payments.values():
            if infos['status'] != self.STATUS.COMPLETED:
                return False
        return True

    def is_failed(self):
        for infos in self.payments.values():
            if infos['status'] == self.STATUS.FAILED:
                return True
        return False

    def is_refunded(self):
        for infos in self.payments.values():
            if infos['status'] == self.STATUS.REFUNDED:
                return True
        return False

    def calculate_payout_price(self):
        return round(self.OUR_FEE_INVERSED * (self.total - self.OUR_FLAT - self.OUR_FLAT * self.group.users.count()), 2)

    def calculate_paypal_part(self):
        return round(self.total - self.PAYMENT_FEE_INVERSED * (self.total - self.PAYOUT_FLAT - self.CHECKOUT_FLAT * self.group.users.count()), 2)

    def calculate_profit(self):
        return round(self.total - self.calculate_payout_price() - self.calculate_paypal_part(), 2)

    def __str__(self):
        return str(self.id)

    class Meta:
        pass
