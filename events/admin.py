from django.contrib import admin

from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "view_project_name",
        "timestamp",
        "resolved"
    )

    fields = (
        "id",
        "view_project_name",
        "message",
        "timestamp",
        "resolved",
        "created_at",
        "updated_at"
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(ordering='project__name', description="Project")
    def view_project_name(self, obj):
        return obj.project.name


admin.site.register(Event, EventAdmin)
