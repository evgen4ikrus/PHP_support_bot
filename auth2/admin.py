from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from auth2.forms import Auth2UserCreationForm, TelegramUserChangeForm
from auth2.models import StaffUser, TelegramUser, ClientProfile, FreelancerProfile


class ClientInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    readonly_fields = ("orders_created", "orders_in_progress", "orders_done")
    verbose_name_plural = "Клиенты"


class FreelancerInline(admin.StackedInline):
    model = FreelancerProfile
    can_delete = False
    readonly_fields = ("jobs_done",)
    verbose_name_plural = "Фрилансеры"


class UserAdmin(BaseUserAdmin):
    add_form = Auth2UserCreationForm
    fieldsets = (
        (None, {"fields": ("tg_chat_id", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active",)}),
    )
    search_fields = (
        "tg_chat_id",
        "email",
    )


@admin.register(StaffUser)
class StaffUserAdmin(UserAdmin):
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("username", "tg_chat_id", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = (
        "username",
        "tg_chat_id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )


@admin.register(TelegramUser)
class TelegramUserAdmin(UserAdmin):
    inlines = (ClientInline, FreelancerInline)
    form = TelegramUserChangeForm
    list_display = (
        "tg_chat_id",
        "first_name",
        "last_name",
        "is_active",
    )
