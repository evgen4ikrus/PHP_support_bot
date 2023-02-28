from django.contrib import admin

from jobs.models import Job, Message


@admin.register(Job)
class JobModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "freelancer",
        "status",
        "deadline",
    )

@admin.register(Message)
class MessageModelAdmin(admin.ModelAdmin):
    list_display = (
        "created",
        "job",
        "sender",
        "message",
    )