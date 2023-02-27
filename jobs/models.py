from __future__ import annotations

import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from django_fsm import FSMField, transition

from jobs.exceptions import DeadlineIsExpired, DeadlineWasAlreadySet


class Job(TimeStampedModel):
    class Statuses(models.TextChoices):
        CREATED = "CREATED", "Создан"
        IN_PROGRESS = "IN_PROGRESS", "В процессе"
        DONE = "DONE", "Выполнен"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Клиент",
    )
    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="jobs",
        verbose_name="Фрилансер",
    )
    status = FSMField("Статус", default=Statuses.CREATED)
    _deadline = models.DateTimeField("Предпологаемая дата выполнения", null=True, blank=True)

    class Meta:
        verbose_name = "Работа"
        verbose_name_plural = "Работы"

    def __str__(self):
        return f"{self.title} [{self.status}]: {self.client} - {self.freelancer}"

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value: datetime.datetime):
        if self._deadline:
            raise DeadlineWasAlreadySet("Вы не можете изменить или удалить дату исполнения")
        elif value <= timezone.now():
            raise DeadlineIsExpired("Вы не можете назначить дату исполнения в прошлом")
        self._deadline = value

    @transition(field=status, source=Statuses.CREATED, target=Statuses.IN_PROGRESS)
    def take(self, freelancer: "auth2.models.TelegramUser", deadline: datetime.datetime) -> Optional[Job]:
        self.deadline = deadline
        self.freelancer = freelancer
        self.save()
        return self

    @transition(field=status, source=Statuses.IN_PROGRESS, target=Statuses.DONE)
    def mark_done(self) -> Optional[Job]:
        return self
