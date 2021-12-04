from django.contrib import admin

from .models import Event, Issue, RawEvent


class RawEventAdmin(admin.ModelAdmin):
    list_display = ("id", "view_project_name", "created_at")

    fields = ("id", "view_project_name", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(ordering="project__name", description="Project")
    def view_project_name(self, obj):
        return obj.project.name


class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "view_project_name", "timestamp", "resolved")

    fields = (
        "id",
        "raw_event",
        "issue",
        "view_project_name",
        "message",
        "timestamp",
        "resolved",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(ordering="project__name", description="Project")
    def view_project_name(self, obj):
        return obj.project.name


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "view_project_name",
        "view_message",
        "first_seen_at",
        "last_seen_at",
        "resolved",
    )

    fields = (
        "id",
        "signature",
        "primary_event",
        "view_project_name",
        "view_message",
        "resolved",
        "created_at",
        "updated_at",
        "resolved_at",
        "first_seen_at",
        "last_seen_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(ordering="project__name", description="Project")
    def view_project_name(self, obj):
        return obj.project.name

    @admin.display(ordering="primary_event__message", description="Message")
    def view_message(self, obj):
        return obj.primary_event.message


admin.site.register(Event, EventAdmin)
admin.site.register(RawEvent, RawEventAdmin)
admin.site.register(Issue, IssueAdmin)
