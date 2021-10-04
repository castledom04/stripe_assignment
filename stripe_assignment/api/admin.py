from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (Account, User, PaymentMethod, Subscription, Customer)


class AccountAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'created_at',
        'updated_at',
    )
    search_fields = [
        'id',
        'name',
    ]


class UserAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'username',
        'account',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = [
        'id',
        'username',
        'email',
        'account__id',
        'account__name',
    ]
    list_filter = [
        'account',
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if "password" in form.changed_data:
            obj.refresh_from_db()
            obj.set_password(form.data.get('password'))
            obj.save()


class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'id_reference',
        'is_active',
        'account',
        'created_at',
        'updated_at'
    )
    search_fields = [
        'id',
        'id_reference',
        'account__id',
        'account__name',
    ]
    list_filter = [
        'account',
    ]


class PaymentMethodAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'id_reference',
        'is_active',
        'type',
        'account',
        'created_at',
        'updated_at'
    )
    search_fields = [
        'id',
        'id_reference',
        'account__id',
        'account__name',
    ]
    list_filter = [
        'account',
        'type',
    ]


class SubscriptionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'id_reference',
        'status',
        'payment_gateway_status',
        'current_period_start',
        'current_period_end',
        'price_reference',
        'purchase_date',
        'account',
        'created_at',
        'updated_at'
    )
    search_fields = [
        'id',
        'id_reference',
        'account__id',
        'account__name',
    ]
    list_filter = [
        'account',
        'status',
        'payment_gateway_status',
    ]


admin.site.register(Account, AccountAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.unregister(Group)
