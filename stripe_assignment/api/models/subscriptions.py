import uuid

from django.db import models

from .constants import PaymentMethodType, SubscriptionStatus
from .mixins import TimeStampMixin


class Customer(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField('Is active', default=True)
    id_reference = models.CharField('Id reference', max_length=50, blank=False, default='')
    account = models.ForeignKey(
        'api.Account', null=False, related_name='customers',
        verbose_name="Customer", on_delete=models.CASCADE
    )


class PaymentMethod(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField('Is active', default=True)
    id_reference = models.CharField('Id reference', max_length=50, blank=False, default='')
    type = models.CharField('Type', max_length=50, blank=False, default=PaymentMethodType.CARD)
    account = models.ForeignKey(
        'api.Account', null=False, related_name='payment_methods',
        verbose_name="PaymentMethod", on_delete=models.CASCADE
    )


class Subscription(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField('Status', max_length=50, blank=False, default=SubscriptionStatus.PENDING)
    payment_gateway_status = models.CharField('Payment gateway status', max_length=50, blank=True, default='')
    current_period_start = models.DateTimeField('current_period_start', default=None, blank=True, null=True)
    current_period_end = models.DateTimeField('current_period_end', default=None, blank=True, null=True)
    id_reference = models.CharField('Id reference', max_length=50, blank=True, default='')
    price_reference = models.CharField('Price reference', max_length=50, blank=False, default='')
    account = models.ForeignKey(
        'api.Account', null=False, related_name='subscriptions',
        verbose_name="Subscription", on_delete=models.CASCADE
    )

    @property
    def purchase_date(self):
        return self.created_at.date()
