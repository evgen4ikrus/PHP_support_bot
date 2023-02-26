from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from django_fsm import FSMField

from auth2.models import User, Client


class Product(TimeStampedModel):
    title = models.CharField("Наименование", max_length=30)
    price = models.DecimalField("Стоимость", max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.title} - {self.price}"

    def buy(self, user: User) -> Purchase:
        return Purchase.objects.create(
            user=user,
            product=self,
            price=self.price,
            status=Purchase.Statuses.SUCCESS
        )


class Subscription(Product):
    description = models.TextField("Описание", blank="", default="")
    orders_amount = models.PositiveSmallIntegerField("Количество заказов")
    can_conversate_freelancer = models.BooleanField("Может общаться с фрилансером", default=False)
    can_stick_to_freelancer = models.BooleanField("Может закрепиться за фрилансером", default=False)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.title} - {self.price}"

    @classmethod
    def user_has_active_subscription(cls, user: User) -> Optional[Purchase]:
        last_purchase = Purchase.objects.filter(user=user).last()
        if last_purchase and last_purchase.created >= timezone.now() - timezone.timedelta(days=30):
            return last_purchase

    @classmethod
    def user_can_subscribe(cls, client: Client) -> bool:
        result = False
        user_has_money = True
        if not client.can_create_order and user_has_money:
            result = True
        return result

    def subscribe(self, client: Client) -> Optional[Purchase]:
        if self.user_can_subscribe(client):
            return self.buy(client)


class Purchase(TimeStampedModel):
    class Statuses(models.TextChoices):
        PROCESSING = "PROCESSING", "В обработке"
        CANCELED = "CANCELED", "Отменено"
        FAILED = "FAILED", "Ошибка"
        SUCCESS = "SUCCESS", "Успешно"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchases",
        verbose_name="Покупатель",
    )
    product = models.ForeignKey(
        "products.Product",
        null=True,
        on_delete=models.SET_NULL,
        related_name="purchases",
        verbose_name="Продукт",
    )
    status = FSMField("Статус", default=Statuses.PROCESSING)
    price = models.DecimalField("Стоимость", max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

    def __str__(self):
        return f"{self.pk}: [{self.status}] {self.user} - {self.product} = {self.price}"
