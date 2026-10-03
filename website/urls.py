from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("sign-in/", views.owner_sign_in, name="owner_sign_in"),
    path("sign-out/", views.owner_sign_out, name="owner_sign_out"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard),
    path("dashboard/projects/", views.dashboard_projects, name="dashboard_projects"),
    path("dashboard/projects/create/", views.project_create, name="dashboard_project_create"),
    path("dashboard/tech-stacks/", views.dashboard_tech_stacks, name="dashboard_tech_stacks"),
    path("dashboard/tech-stacks/create/", views.tech_stack_create, name="tech_stack_create"),

    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),

    path("inquiry/", views.inquiry_create, name="inquiry_create"),
    path("inquiry/success/", views.inquiry_success, name="inquiry_success"),

    path(
        "testimonies/",
        views.TestimonyListView.as_view(),
        name="testimony_list",
    ),

    path(
        "testimonies/create/",
        views.testimony_create,
        name="testimony_create",
    ),

    path(
        "testimonies/<int:pk>/",
        views.testimony_detail,
        name="testimony_detail",
    ),
]
