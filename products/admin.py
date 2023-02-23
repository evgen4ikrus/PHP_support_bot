from django.contrib import admin

from products.models import Subscription


@admin.register(Subscription)
class SubscriptionModelAdmin(admin.ModelAdmin):
    pass
