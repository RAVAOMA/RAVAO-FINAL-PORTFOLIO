from django.contrib import admin
from .models import (
    PersonalInformation,
    Project,
    Inquiry,
    Testimony,
)

admin.site.register(PersonalInformation)
admin.site.register(Project)
admin.site.register(Inquiry)
admin.site.register(Testimony)

