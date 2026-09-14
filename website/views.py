from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView

from .models import PersonalInformation, Project, Testimony
from .forms import ProjectForm, InquiryForm, TestimonyForm

def home(request):
    personal = PersonalInformation.objects.first()
    projects = Project.objects.order_by("-pk")

    return render(request, "website/index.html", {
        "personal": personal,
        "projects": projects,
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

def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("project_list")
    else:
        form = ProjectForm()

    return render(
        request,
        "website/project_form.html",
        {"form": form},
    )


def inquiry_create(request):
    if request.method == "POST":
        form = InquiryForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("inquiry_success")
    else:
        form = InquiryForm()

    return render(
        request,
        "website/inquiry_form.html",
        {"form": form},
    )


def inquiry_success(request):
    return render(request, "website/inquiry_success.html")


def testimony_create(request):
    if request.method == "POST":
        form = TestimonyForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("testimony_list")
    else:
        form = TestimonyForm()

    return render(
        request,
        "website/testimony_form.html",
        {"form": form},
    )

class TestimonyListView(ListView):
    model = Testimony
    template_name = "website/testimony_list.html"
    context_object_name = "testimonies"

def testimony_detail(request, pk):
    testimony = get_object_or_404(Testimony, pk=pk)

    return render(request, "website/testimony_detail.html", {
        "testimony": testimony,
    })


