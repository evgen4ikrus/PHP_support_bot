from django.contrib import admin

from jobs.models import Job


@admin.register(Job)
class JobModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "freelancer",
        "status",
        "deadline",
    )
