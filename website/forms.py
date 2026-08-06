from django import forms

from .models import Inquiry, Project, Testimony

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "project_name",
            "description",
            "tech_stack",
            "link",
        ]

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = [
            "first_name",
            "last_name",
            "contact_number",
            "email",
            "address",
            "message",
        ]

class TestimonyForm(forms.ModelForm):
    class Meta:
        model = Testimony
        fields = [
            "full_name",
            "content",
        ]


