from django.contrib import admin

from .models import Project, Event


class ProjectAdmin(admin.ModelAdmin):
    fields = ("title", "public_key", "created_at", "updated_at")
    readonly_fields = ("public_key", "created_at", "updated_at")
    list_display = ("title",)


admin.site.register(Project, ProjectAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "view_project_title",
        "timestamp"
    )

    fields = (
        "id",
        "view_project_title",
        "timestamp",
        "created_at",
        "updated_at"
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(ordering='project__title', description="Project")
    def view_project_title(self, obj):
        return obj.project.title


admin.site.register(Event, EventAdmin)
