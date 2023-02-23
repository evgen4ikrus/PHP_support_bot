from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Types(models.TextChoices):
        CLIENT = "CLIENT", "Клиент"
        FREELANCER = "FREELANCER", "Фрилансер"
        STAFF = "STAFF", "Cотрудник"

    tg_chat_id = models.CharField(_("Телеграм чат ID"), max_length=30)
    type = models.CharField(
        _("Тип пользователя"),
        max_length=50,
        choices=Types.choices,
        default=Types.STAFF
    )

    base_type = Types.STAFF


class NonStaffUsers(User):
    """The only difference is redefined saving process for non-staff users."""

    def save_user_with_initial_data(self, *args, **kwargs):
        """Create a user with initial data"""
        self.type = self.base_type
        self.is_active = False
        return super().save(*args, **kwargs)

    def create_profile(self) -> None:
        if self.type == self.Types.CLIENT:
            ClientProfile.objects.create(user=self)
        elif self.type == self.Types.FREELANCER:
            FreelancerProfile.objects.create(user=self)

    def save(self, *args, **kwargs):
        """Redefine the save method
        Creation: save a telegram chat id as a username; define a user type; create a user profile;
        Modifying: changing a telegram chat id changes a username field
        """
        if not self.pk:
            self.tg_chat_id = self.username
            self.save_user_with_initial_data(self, *args, **kwargs)
            self.create_profile()
        else:
            self.username = self.tg_chat_id
            return super().save(*args, **kwargs)


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Клиент"
    )
    orders_left = models.PositiveSmallIntegerField(default=0, verbose_name="Заказы остаток")

    # TODO: add a plan field

    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"

    def __str__(self):
        return self.user.username


class FreelancerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Фрилансер"
    )
    orders_done = models.PositiveSmallIntegerField(default=0, verbose_name="Заказы выполненные")

    # TODO: add a payrate field

    class Meta:
        verbose_name = "Профиль фрилансера"
        verbose_name_plural = "Профили фрилансеров"

    def __str__(self):
        return self.user.username


class StaffManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(type=User.Types.STAFF)


class ClientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(type=User.Types.CLIENT)


class FreelancerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(type=User.Types.FREELANCER)


class Staff(User):
    base_type = User.Types.STAFF
    objects = StaffManager()

    class Meta:
        proxy = True
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Client(NonStaffUsers):
    base_type = User.Types.CLIENT
    objects = ClientManager()

    class Meta:
        proxy = True
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    @property
    def profile(self):
        return self.clientprofile


class Freelancer(NonStaffUsers):
    base_type = User.Types.FREELANCER
    objects = FreelancerManager()

    class Meta:
        proxy = True
        verbose_name = "Фрилансер"
        verbose_name_plural = "Фрилансеры"

    @property
    def profile(self):
        return self.freelancerprofile
