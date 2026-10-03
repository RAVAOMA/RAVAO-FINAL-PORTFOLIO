from django.db import models
from django.db.models.functions import Lower

class PersonalInformation(models.Model):
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    summary = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TechStack(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_tech_stack_name_ci"),
        ]

    def clean(self):
        super().clean()
        self.name = " ".join(self.name.split())

    def __str__(self):
        return self.name


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    description = models.TextField()
    tech_stacks = models.ManyToManyField(TechStack, related_name="projects")
    link = models.URLField()

    def __str__(self):
        return self.project_name

    @property
    def tech_stack_names(self):
        return ", ".join(stack.name for stack in self.tech_stacks.all())
    
class Inquiry(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    message = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Testimony(models.Model):
    full_name = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.full_name
    
