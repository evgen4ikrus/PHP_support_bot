from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from jobs.models import Job


class StaffUserManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(is_staff=True)


class TelegramUserManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(is_staff=False, is_superuser=False)


class User(AbstractUser):
    tg_chat_id = models.CharField(_("Телеграм чат ID"), max_length=30)


class TelegramUser(User):
    """The only difference is redefined saving process for non-staff users."""
    objects = TelegramUserManager()

    class Meta:
        proxy = True
        verbose_name = "Обычный пользователь"
        verbose_name_plural = "Обычные пользователи"

    def save(self, *args, **kwargs):
        """Redefine the save method
        Creation: make tg_chat_id and username equal; define a user type; create a user profiles;
        Modifying: changing a telegram chat id changes a username field
        """
        if not self.pk:
            if self.username:
                self.tg_chat_id = str(self.username)
            elif self.tg_chat_id:
                self.username = str(self.tg_chat_id)
            super().save(*args, **kwargs)
            self.is_active = False
            self.save()
            ClientProfile.objects.create(user=self)
            FreelancerProfile.objects.create(user=self)
        else:
            self.username = str(self.tg_chat_id)
            return super().save(*args, **kwargs)


class ClientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Клиент"
    )

    class Meta:
        verbose_name = "Профиль клиента"
        verbose_name_plural = "Профили клиентов"

    def __str__(self):
        return self.user.username

    @property
    @admin.display(
        description='Заказов всего',
    )
    def orders_created(self):
        return Job.objects.filter(client=self.user, status=Job.Statuses.CREATED).count()

    @property
    @admin.display(
        description='Заказов в процессе',
    )
    def orders_in_progress(self):
        return Job.objects.filter(client=self.user, status=Job.Statuses.IN_PROGRESS).count()

    @property
    @admin.display(
        description='Заказов выполненных',
    )
    def orders_done(self):
        return Job.objects.filter(client=self.user, status=Job.Statuses.DONE).count()


class FreelancerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Фрилансер"
    )
    payrate = models.ForeignKey(
        "payrates.Payrate",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Ставка оклада"
    )

    class Meta:
        verbose_name = "Профиль фрилансера"
        verbose_name_plural = "Профили фрилансеров"

    def __str__(self):
        return self.user.username

    @property
    @admin.display(
        description='Количество выполненных заказов',
    )
    def jobs_done(self):
        return Job.objects.filter(freelancer=self.user, status=Job.Statuses.DONE).count()


class StaffUser(User):
    objects = StaffUserManager()

    class Meta:
        proxy = True
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Client(TelegramUser):
    class Meta:
        proxy = True
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    @property
    def profile(self):
        return self.clientprofile

    def orders_left(self) -> int:
        from products.models import Subscription
        result = 0
        purchase = Subscription.user_has_active_subscription(self)
        if purchase:
            start_date = purchase.created
            end_date = start_date + timezone.timedelta(days=30)
            orders_created = Job.objects.filter(client=self, created__range=(start_date, end_date)).count()
            result = purchase.product.subscription.orders_amount - orders_created
        return result

    def can_create_order(self) -> bool:
        return self.orders_left() > 0 and self.is_active

    def get_my_orders(self, page_number: int = 1) -> Paginator:
        jobs = Job.objects.filter(client=self).order_by('id')
        paginator = Paginator(jobs, 5)
        return paginator.get_page(page_number)


class Freelancer(TelegramUser):
    class Meta:
        proxy = True
        verbose_name = "Фрилансер"
        verbose_name_plural = "Фрилансеры"

    @property
    def profile(self):
        return self.freelancerprofile

    @staticmethod
    def get_job_list(page_number: int = 1) -> Paginator:
        jobs = Job.objects.filter(status=Job.Statuses.CREATED).order_by('id')
        paginator = Paginator(jobs, 5)
        return paginator.get_page(page_number)
