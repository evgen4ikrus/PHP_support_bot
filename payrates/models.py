from django.db import models


class Payrate(models.Model):
    title = models.CharField("Название", max_length=60)
    total_amount = models.DecimalField("Сумма", max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = "Тариф оплаты"
        verbose_name_plural = "Тарифы оплат"

    def __str__(self):
        return f"{self.title} - {self.total_amount}"
