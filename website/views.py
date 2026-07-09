from django.shortcuts import render, get_object_or_404
from .models import PersonalInformation, Project


def home(request):
    personal = PersonalInformation.objects.first()

    return render(request, "website/index.html", {
        "personal": personal,
    })


def project_list(request):
    projects = Project.objects.all()

    return render(request, "website/project_list.html", {
        "projects": projects,
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    return render(request, "website/project_detail.html", {
        "project": project,
    })