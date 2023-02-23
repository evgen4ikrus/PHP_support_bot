from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from auth2.forms import Auth2UserCreationForm
from auth2.models import Freelancer, Client, ClientProfile, FreelancerProfile, Staff


class UserAdmin(BaseUserAdmin):
    add_form = Auth2UserCreationForm
    readonly_fields = ("type",)
    fieldsets = (
        (None, {"fields": ("type", "tg_chat_id", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active",)}),
    )
    search_fields = (
        "tg_chat_id",
        "first_name",
        "last_name",
        "email",
    )
    list_display = (
        "username",
        "tg_chat_id",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )


class StaffUserAdmin(UserAdmin):
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("username", "type", "tg_chat_id", "password")}),
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


class ClientInline(admin.StackedInline):
    model = ClientProfile
    can_delete = False
    readonly_fields = ("orders_left",)
    verbose_name_plural = "Клиенты"


class ClientUserAdmin(UserAdmin):
    inlines = (ClientInline,)
    list_display = (
        "tg_chat_id",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )


class FreelancerInline(admin.StackedInline):
    model = FreelancerProfile
    can_delete = False
    readonly_fields = ("orders_done",)
    verbose_name_plural = "Фрилансеры"


class FreelancerUserAdmin(UserAdmin):
    inlines = (FreelancerInline,)
    list_display = (
        "tg_chat_id",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )


admin.site.register(Staff, StaffUserAdmin)
admin.site.register(Client, ClientUserAdmin)
admin.site.register(Freelancer, FreelancerUserAdmin)
