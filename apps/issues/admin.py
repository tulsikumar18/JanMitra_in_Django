from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Issue

from .models import IssueStatusHistory


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "citizen",
        "category",
        "status",
        "location",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "title",
        "description",
        "location",
    )




@admin.register(IssueStatusHistory)
class IssueStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "issue",
        "old_status",
        "new_status",
        "changed_by",
        "created_at",
    )

    list_filter = (
        "old_status",
        "new_status",
        "created_at",
    )

    search_fields = (
        "issue__title",
        "changed_by__email",
        "note",
    )

    ordering = (
        "-created_at",
    )