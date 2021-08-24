from django.contrib import admin

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    fields = ("name", "public_key", "created_at", "updated_at")
    readonly_fields = ("public_key", "created_at", "updated_at")
    list_display = ("name",)


admin.site.register(Project, ProjectAdmin)
