import re

from django.db import migrations, models
from django.db.models.functions import Lower


def copy_legacy_stacks(apps, schema_editor):
    Project = apps.get_model("website", "Project")
    TechStack = apps.get_model("website", "TechStack")
    alias = schema_editor.connection.alias
    for project in Project.objects.using(alias).all().iterator():
        raw = project.tech_stack.strip()
        # Earlier records used comma-separated names or whitespace-separated tokens.
        names = re.split(r"[,;|\n]+", raw) if re.search(r"[,;|\n]", raw) else raw.split()
        for name in names:
            name = " ".join(name.split())
            if not name:
                continue
            stack = TechStack.objects.using(alias).filter(name__iexact=name).first()
            if stack is None:
                stack = TechStack.objects.using(alias).create(name=name)
            # SQLite may defer the new join-table unique index until this migration
            # finishes, so do not rely on add(ignore_conflicts=True) to deduplicate.
            Project.tech_stacks.through.objects.using(alias).get_or_create(
                project_id=project.pk, techstack_id=stack.pk,
            )


def restore_legacy_stacks(apps, schema_editor):
    Project = apps.get_model("website", "Project")
    alias = schema_editor.connection.alias
    for project in Project.objects.using(alias).prefetch_related("tech_stacks").iterator(chunk_size=100):
        project.tech_stack = ", ".join(stack.name for stack in project.tech_stacks.all())[:255]
        project.save(using=alias, update_fields=["tech_stack"])


class Migration(migrations.Migration):
    dependencies = [("website", "0002_inquiry_testimony")]
    operations = [
        migrations.CreateModel(
            name="TechStack",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name", "pk"],
                "constraints": [models.UniqueConstraint(Lower("name"), name="unique_tech_stack_name_ci")],
            },
        ),
        migrations.AddField(
            model_name="project", name="tech_stacks",
            field=models.ManyToManyField(related_name="projects", to="website.techstack"),
        ),
        migrations.RunPython(copy_legacy_stacks, restore_legacy_stacks),
        migrations.RemoveField(model_name="project", name="tech_stack"),
    ]
