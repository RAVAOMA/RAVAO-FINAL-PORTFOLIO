from django.test import Client, TestCase
from django.urls import reverse

from .models import Inquiry, Project, Testimony


class PortfolioFlowTests(TestCase):
    project_data = {
        "project_name": "Database-backed Portfolio",
        "description": "A project added through the portfolio form.",
        "tech_stack": "Python Django SQLite",
        "link": "https://example.com/portfolio",
    }
    inquiry_data = {
        "first_name": "Alex",
        "last_name": "Santos",
        "contact_number": "09171234567",
        "email": "alex@example.com",
        "address": "Angeles City",
        "message": "I would like to ask about your projects.",
    }

    def test_home_has_an_empty_state_instead_of_placeholder_projects(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "No projects have been added yet.")
        self.assertNotContains(response, "Arduino Embedded System")
        self.assertNotContains(response, "Future Django Web Application")
        self.assertContains(response, reverse("project_create"))

    def test_created_and_updated_projects_appear_on_the_homepage(self):
        response = self.client.post(reverse("project_create"), self.project_data)
        self.assertRedirects(response, reverse("project_list"))

        project = Project.objects.get()
        homepage = self.client.get(reverse("home"))
        for field in ("project_name", "description", "tech_stack", "link"):
            self.assertContains(homepage, getattr(project, field))
        self.assertContains(homepage, reverse("project_detail", args=[project.pk]))

        project.project_name = "Updated Portfolio Project"
        project.save()
        homepage = self.client.get(reverse("home"))
        self.assertContains(homepage, project.project_name)
        self.assertNotContains(homepage, self.project_data["project_name"])

    def test_invalid_project_is_not_saved(self):
        data = {**self.project_data, "link": "not-a-url"}
        response = self.client.post(reverse("project_create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("link", response.context["form"].errors)
        self.assertEqual(Project.objects.count(), 0)

    def test_contact_requires_csrf_and_saves_a_valid_inquiry(self):
        client = Client(enforce_csrf_checks=True)
        url = reverse("inquiry_create")
        form_page = client.get(url)

        self.assertContains(form_page, 'action="' + url + '"')
        for field in self.inquiry_data:
            self.assertContains(form_page, 'name="' + field + '"')
        self.assertEqual(Inquiry.objects.count(), 0)

        rejected = client.post(url, self.inquiry_data)
        self.assertEqual(rejected.status_code, 403)
        self.assertEqual(Inquiry.objects.count(), 0)

        response = client.post(url, {
            **self.inquiry_data,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })
        self.assertRedirects(response, reverse("inquiry_success"))
        inquiry = Inquiry.objects.get()
        for field, value in self.inquiry_data.items():
            self.assertEqual(getattr(inquiry, field), value)

    def test_invalid_contact_preserves_input_and_displays_errors(self):
        data = {**self.inquiry_data, "email": "invalid-email", "message": ""}
        response = self.client.post(reverse("inquiry_create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 0)
        self.assertIn("email", response.context["form"].errors)
        self.assertIn("message", response.context["form"].errors)
        self.assertContains(response, 'value="Alex"')
        self.assertContains(response, 'value="invalid-email"')
        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, "This field is required.")

    def test_testimony_can_be_created_listed_and_opened(self):
        response = self.client.post(reverse("testimony_create"), {
            "full_name": "Jamie Cruz",
            "content": "The project was clearly presented.",
        })
        self.assertRedirects(response, reverse("testimony_list"))

        testimony = Testimony.objects.get()
        detail_url = reverse("testimony_detail", args=[testimony.pk])
        listing = self.client.get(reverse("testimony_list"))
        self.assertContains(listing, testimony.full_name)
        self.assertContains(listing, detail_url)

        detail = self.client.get(detail_url)
        self.assertContains(detail, testimony.full_name)
        self.assertContains(detail, testimony.content)
        self.assertTemplateUsed(detail, "website/testimony_detail.html")

    def test_invalid_testimony_is_not_saved(self):
        response = self.client.post(reverse("testimony_create"), {
            "full_name": "Jamie Cruz",
            "content": "",
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response.context["form"].errors)
        self.assertEqual(Testimony.objects.count(), 0)

    def test_unknown_detail_pages_return_404(self):
        for name in ("project_detail", "testimony_detail"):
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=[999999]))
                self.assertEqual(response.status_code, 404)

    def test_required_navigation_is_available_on_each_page(self):
        project = Project.objects.create(**self.project_data)
        testimony = Testimony.objects.create(full_name="Jamie", content="Thank you.")
        pages = [
            reverse("home"),
            reverse("project_list"),
            reverse("project_create"),
            reverse("project_detail", args=[project.pk]),
            reverse("inquiry_create"),
            reverse("inquiry_success"),
            reverse("testimony_list"),
            reverse("testimony_create"),
            reverse("testimony_detail", args=[testimony.pk]),
        ]
        destinations = ("project_create", "inquiry_create", "testimony_list")
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                for destination in destinations:
                    self.assertContains(response, 'href="' + reverse(destination) + '"')
