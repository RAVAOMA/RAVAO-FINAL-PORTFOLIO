from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("projects/", views.project_list, name="project_list"),

    path("projects/<int:pk>/", views.project_detail, name="project_detail"),

    path("projects/create/", views.project_create, name="project_create"),

    path("inquiry/", views.inquiry_create, name="inquiry_create"),

    path("inquiry/success/", views.inquiry_success, name="inquiry_success"),

    path("testimonies/create/", views.testimony_create, name="testimony_create"),
]

