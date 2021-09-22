from django.contrib import admin

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    fields = ("name", "public_key", "sentry_dsn", "created_at", "updated_at")
    readonly_fields = ("public_key", "created_at", "updated_at")
    list_display = ("name",)

    def has_add_permission(self, request):
        return False


admin.site.register(Project, ProjectAdmin)
