from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Inquiry, Project, TechStack, Testimony
from .widgets import TechStackRadioGroups


class OwnerAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Sign-in failed. Use an active superuser account and the correct password.",
        "inactive": "Sign-in failed. Use an active superuser account and the correct password.",
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise forms.ValidationError(self.error_messages["invalid_login"], code="invalid_login")


class TechStackForm(forms.ModelForm):
    class Meta:
        model = TechStack
        fields = ["name"]
        labels = {"name": "Tech Stack Name"}
        widgets = {"name": forms.TextInput(attrs={"placeholder": "e.g. Python", "autofocus": True})}

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if TechStack.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This tech stack already exists. Reuse it when creating a project.")
        return name

class ProjectForm(forms.ModelForm):
    tech_stacks = forms.ModelMultipleChoiceField(
        queryset=TechStack.objects.all(),
        widget=TechStackRadioGroups,
        label="Tech Stacks",
        help_text="Choose one stack per group. Add another group if this project uses more than one.",
    )

    class Meta:
        model = Project
        fields = [
            "project_name",
            "description",
            "tech_stacks",
            "link",
        ]
        labels = {"project_name": "Project Name", "description": "Project Description", "link": "Link"}
        widgets = {
            "project_name": forms.TextInput(attrs={"placeholder": "Give your project a name"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "What did you build?"}),
            "link": forms.URLInput(attrs={"placeholder": "https://example.com/my-project"}),
        }

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

