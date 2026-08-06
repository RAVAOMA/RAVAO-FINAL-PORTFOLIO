from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

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
        views.TestimonyDetailView.as_view(),
        name="testimony_detail",
    ),
]

