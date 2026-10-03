from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import IntegrityError, transaction
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from .models import PersonalInformation, Project, TechStack, Testimony
from .forms import OwnerAuthenticationForm, ProjectForm, InquiryForm, TechStackForm, TestimonyForm
from .decorators import owner_required


@never_cache
@require_http_methods(["GET", "POST"])
def owner_sign_in(request):
    if request.user.is_authenticated and request.user.is_active and request.user.is_superuser:
        return redirect("dashboard")
    form = OwnerAuthenticationForm(request, data=request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("dashboard")
    return render(request, "website/sign_in.html", {"form": form})


@require_POST
def owner_sign_out(request):
    logout(request)
    return redirect("home")


@never_cache
@owner_required
def dashboard(request):
    return render(request, "website/dashboard.html", {
        "project_count": Project.objects.count(),
        "tech_stack_count": TechStack.objects.count(),
        "recent_projects": Project.objects.prefetch_related("tech_stacks").order_by("-pk")[:5],
        "active_page": "overview",
    })


@never_cache
@owner_required
def dashboard_projects(request):
    return render(request, "website/dashboard_projects.html", {
        "projects": Project.objects.prefetch_related("tech_stacks").order_by("-pk"),
        "active_page": "projects",
    })


@never_cache
@owner_required
def dashboard_tech_stacks(request):
    return render(request, "website/dashboard_tech_stacks.html", {
        "tech_stacks": TechStack.objects.prefetch_related("projects"),
        "active_page": "tech_stacks",
    })


@never_cache
@owner_required
@require_http_methods(["GET", "POST"])
def tech_stack_create(request):
    form = TechStackForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            form.add_error("name", "This tech stack already exists. Please use the existing one.")
        else:
            messages.success(request, "Tech stack added. It is ready to use in your projects.")
            return redirect("dashboard_tech_stacks")
    return render(request, "website/tech_stack_form.html", {"form": form, "active_page": "tech_stacks"})

def home(request):
    personal = PersonalInformation.objects.first()
    projects = Project.objects.prefetch_related("tech_stacks").order_by("-pk")

    return render(request, "website/index.html", {
        "personal": personal,
        "projects": projects,
    })


def project_list(request):
    projects = Project.objects.prefetch_related("tech_stacks").order_by("-pk")

    return render(request, "website/project_list.html", {
        "projects": projects,
    })


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related("tech_stacks"), pk=pk)

    return render(request, "website/project_detail.html", {
        "project": project,
    })

@never_cache
@owner_required
@require_http_methods(["GET", "POST"])
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, "Project published. It now appears on your portfolio.")
            return redirect("dashboard_projects")
    else:
        form = ProjectForm()

    return render(
        request,
        "website/project_form.html",
        {"form": form, "has_tech_stacks": TechStack.objects.exists(), "active_page": "projects"},
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

