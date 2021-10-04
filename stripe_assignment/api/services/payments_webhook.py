from datetime import datetime

import pytz
import stripe
from django.conf import settings

from ..models import Customer, Subscription
from ..models.constants import SubscriptionStatus


class PaymentsWebhook:

    def __init__(self):
        stripe.api_key = settings.STRIPE_API_SECRET
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def handle_event(self, request):
        if self.webhook_secret:
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.body, sig_header=signature, secret=self.webhook_secret)
                data = event['data']
            except Exception as e:
                return e
            event_type = event['type']
        else:
            data = request.data['data']
            event_type = request.data['type']

        if event_type == 'customer.subscription.created':
            self.__update_subscription_info(data)
            return

        if event_type == 'customer.subscription.updated':
            self.__update_subscription_info(data)
            return

    def __update_subscription_info(self, data):
        subscription = None
        customer = Customer.objects.filter(id_reference=data['object']['customer']).first()
        if customer:
            subscription = Subscription.objects.filter(account=customer.account).first()

        if subscription:
            status = SubscriptionStatus.SUCCESSFUL if data['object']['status'] == 'active' else SubscriptionStatus.FAILED
            timezone = pytz.timezone("UTC")
            current_period_start = timezone.localize(datetime.fromtimestamp(data['object']['current_period_start']))
            current_period_end = timezone.localize(datetime.fromtimestamp(data['object']['current_period_end']))
            subscription.status = status
            subscription.payment_gateway_status = data['object']['status']
            subscription.id_reference = data['object']['id']
            subscription.current_period_start = current_period_start
            subscription.current_period_end = current_period_end
            subscription.save()
