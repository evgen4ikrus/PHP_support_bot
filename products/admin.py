from django.contrib import admin

from products.models import Subscription, Purchase


@admin.register(Subscription)
class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "orders_amount",
        "price",
        "can_stick_to_freelancer",
        "can_conversate_freelancer",
    )


@admin.register(Purchase)
class PurchaseModelAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "price",
        "status",
    )
