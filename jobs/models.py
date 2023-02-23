from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_fsm import FSMField


class Job(TimeStampedModel):
    class Statuses(models.TextChoices):
        CREATED = "CREATED", "Создан"
        IN_PROGRESS = "IN_PROGRESS", "В процессе"
        CANCELED = "CANCELED", "Отменен"
        FAILED = "FAILED", "Провален"
        DONE = "DONE", "Выполнен"

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Клиент",
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Клиент",
    )
    status = FSMField("Статус", default=Statuses.CREATED)
    tg_chat_id = models.CharField("Телеграм чат ID", max_length=30)
    deadline = models.DateTimeField("Предпологаемая дата выполнения")

    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"

    def __str__(self):
        return f"{self.pk}: [{self.status}] {self.client} - {self.freelancer}"
