from django.db import models
from django_extensions.db.models import TimeStampedModel


class Product(TimeStampedModel):
    title = models.CharField("Наименование", max_length=30)
    price = models.DecimalField("Стоимость", max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.title} - {self.price}"


class Subscription(Product):
    description = models.TextField("Описание", blank="", default="")
    orders_amount = models.PositiveSmallIntegerField("Количество заказов")
    can_conversate_freelancer = models.BooleanField("Может общаться с фрилансером", default=False)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.title} - {self.price}"
