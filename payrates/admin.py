from django.contrib import admin

from payrates.models import Payrate


@admin.register(Payrate)
class PayrateModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "total_amount",
    )
