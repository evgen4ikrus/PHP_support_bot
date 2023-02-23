from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_fsm import FSMField


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
