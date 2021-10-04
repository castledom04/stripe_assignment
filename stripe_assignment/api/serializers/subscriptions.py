from django.utils import timezone
from rest_framework import serializers

from ..models import Subscription
from ..models.constants import SubscriptionProduct


class SubscribeSerializer(serializers.Serializer):
    subscription_product = serializers.CharField(max_length=50, allow_null=False)
    card_number = serializers.CharField(min_length=16, max_length=16, allow_null=False)
    card_expiration_month = serializers.IntegerField(min_value=1, max_value=12, allow_null=False)
    card_expiration_year = serializers.IntegerField(min_value=2000, max_value=3000, allow_null=False)
    card_cvc = serializers.IntegerField(min_value=100, max_value=999, allow_null=False)

    def validate_card_number(self, value):

        if not value.isnumeric():
            raise serializers.ValidationError("Card number must be numeric.")

        return value

    def validate_subscription_product(self, value):

        if value not in SubscriptionProduct.get_products():
            raise serializers.ValidationError("Subscription product does not exist.")

        return value

    def validate(self, data):
        new_data = super().validate(data)
        errors = {}
        now = timezone.now()
        if all([
            new_data.get('card_expiration_month') < now.month,
            new_data.get('card_expiration_year') < now.year,
        ]):
            errors['card_expiration_month'] = "Card expiration is past due."
            errors['card_expiration_year'] = "Card expiration is past due."

        if errors:
            raise serializers.ValidationError(errors)

        return new_data


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = [
            'status',
            'payment_gateway_status',
            'current_period_start',
            'current_period_end',
            'id_reference',
            'price_reference',
            'purchase_date',
        ]
