import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from .mixins import TimeStampMixin


class Account(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)

    def __repr__(self):
        return f"<{self.name} ({self.id})>"

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        Account,
        null=False,
        related_name='users',
        verbose_name="Account",
        on_delete=models.CASCADE)

    def get_customer(self):
        return self.account.customers.filter(is_active=True).order_by('created_at').first()

    def get_payment_method(self):
        return self.account.payment_methods.filter(is_active=True).order_by('created_at').first()

    def get_subscription(self):
        return self.account.subscriptions.order_by('created_at').first()

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'
