from django.contrib import admin
from .models import (
    PersonalInformation,
    Project,
    Inquiry,
    Testimony,
    TechStack,
)

admin.site.register(PersonalInformation)
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("project_name", "link")
    filter_horizontal = ("tech_stacks",)


@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


admin.site.register(Inquiry)
admin.site.register(Testimony)
