from django.contrib import admin

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    fields = ("title", "public_key", "created_at", "updated_at")
    readonly_fields = ("public_key", "created_at", "updated_at")
    list_display = ("title",)


admin.site.register(Project, ProjectAdmin)
