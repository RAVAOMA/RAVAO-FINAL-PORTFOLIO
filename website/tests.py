from django.contrib.auth import get_user_model
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from django.utils.text import Truncator

from .models import Inquiry, Project, TechStack, Testimony


class PortfolioFlowTests(TestCase):
    project_data = {
        "project_name": "Database-backed Portfolio",
        "description": "A project added through the portfolio form.",
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

    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser(
            username="portfolio-owner", email="owner@example.com", password="Test-only-password-529!"
        )
        cls.python = TechStack.objects.create(name="Python")
        cls.django = TechStack.objects.create(name="Django")

    def project_post_data(self):
        return {**self.project_data, "tech_stacks_0": str(self.python.pk), "tech_stacks_1": str(self.django.pk)}

    def test_home_has_an_empty_state_instead_of_placeholder_projects(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "No projects have been added yet.")
        self.assertNotContains(response, "Arduino Embedded System")
        self.assertNotContains(response, "Future Django Web Application")
        self.assertContains(response, reverse("owner_sign_in"))
        self.assertNotContains(response, reverse("project_create"))

    def test_created_and_updated_projects_appear_on_the_homepage(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("project_create"), self.project_post_data())
        self.assertRedirects(response, reverse("dashboard_projects"))

        project = Project.objects.get()
        homepage = self.client.get(reverse("home"))
        for field in ("project_name", "description", "tech_stack_names", "link"):
            self.assertContains(homepage, getattr(project, field))
        self.assertContains(homepage, reverse("project_detail", args=[project.pk]))

        project.project_name = "Updated Portfolio Project"
        project.save()
        homepage = self.client.get(reverse("home"))
        self.assertContains(homepage, project.project_name)
        self.assertNotContains(homepage, self.project_data["project_name"])

    def test_invalid_project_is_not_saved(self):
        self.client.force_login(self.owner)
        data = {**self.project_post_data(), "link": "not-a-url"}
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
            reverse("project_detail", args=[project.pk]),
            reverse("inquiry_create"),
            reverse("inquiry_success"),
            reverse("testimony_list"),
            reverse("testimony_create"),
            reverse("testimony_detail", args=[testimony.pk]),
        ]
        destinations = ("owner_sign_in", "inquiry_create", "testimony_list")
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)
                for destination in destinations:
                    self.assertContains(response, 'href="' + reverse(destination) + '"')


class OwnerAccessTests(TestCase):
    password = "Test-only-password-529!"
    protected_names = (
        "dashboard", "dashboard_projects", "dashboard_tech_stacks",
        "project_create", "dashboard_project_create", "tech_stack_create",
    )

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_superuser("owner", "owner@example.com", cls.password)
        cls.regular = User.objects.create_user("regular", password=cls.password)
        cls.staff = User.objects.create_user("staff", password=cls.password, is_staff=True)
        cls.inactive = User.objects.create_superuser("inactive", "inactive@example.com", cls.password, is_active=False)

    def test_sign_in_is_a_dedicated_page(self):
        response = self.client.get(reverse("owner_sign_in"))
        self.assertTemplateUsed(response, "website/sign_in.html")
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_superuser_sign_in_always_redirects_to_dashboard(self):
        response = self.client.post(reverse("owner_sign_in") + "?next=https://example.org", {
            "username": self.owner.username, "password": self.password,
        })
        self.assertRedirects(response, "/dashboard")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.owner.pk)

    def test_regular_staff_inactive_and_bad_password_cannot_sign_in(self):
        attempts = [(user.username, self.password) for user in (self.regular, self.staff, self.inactive)]
        attempts += [(self.owner.username, "wrong-password"), ("missing-user", self.password)]
        for username, password in attempts:
            with self.subTest(username=username):
                response = self.client.post(reverse("owner_sign_in"), {"username": username, "password": password})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Sign-in failed.")
                self.assertNotIn("_auth_user_id", self.client.session)

    def test_empty_sign_in_displays_errors(self):
        response = self.client.post(reverse("owner_sign_in"), {})
        self.assertEqual(set(response.context["form"].errors), {"username", "password"})

    def test_anonymous_cannot_get_or_post_any_management_route(self):
        for name in self.protected_names:
            for method in (self.client.get, self.client.post):
                with self.subTest(name=name, method=method.__name__):
                    response = method(reverse(name), {"name": "Forbidden", "project_name": "Forbidden"})
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(response.url.startswith(reverse("owner_sign_in")))
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(TechStack.objects.count(), 0)

    def test_existing_regular_and_staff_sessions_cannot_bypass_permissions(self):
        for user in (self.regular, self.staff):
            self.client.force_login(user)
            for name in self.protected_names:
                for method in (self.client.get, self.client.post):
                    with self.subTest(user=user.username, name=name, method=method.__name__):
                        self.assertEqual(method(reverse(name), {"name": "Forbidden"}).status_code, 403)
        self.assertEqual(TechStack.objects.count(), 0)

    def test_permission_is_rechecked_after_owner_is_demoted(self):
        self.client.force_login(self.owner)
        self.owner.is_superuser = False
        self.owner.save(update_fields=["is_superuser"])
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)

    def test_owner_can_open_every_management_page(self):
        self.client.force_login(self.owner)
        for name in self.protected_names:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_sign_in_and_management_posts_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("owner_sign_in"), {"username": "owner", "password": self.password})
        self.assertEqual(response.status_code, 403)
        client.get(reverse("owner_sign_in"))
        response = client.post(reverse("owner_sign_in"), {
            "username": "owner", "password": self.password,
            "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
        })
        self.assertRedirects(response, "/dashboard")
        for name in ("project_create", "dashboard_project_create", "tech_stack_create", "owner_sign_out"):
            self.assertEqual(client.post(reverse(name), {"name": "Rejected"}).status_code, 403)
        self.assertEqual(TechStack.objects.count(), 0)

    def test_logout_is_post_only_and_ends_session(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("owner_sign_out")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("owner_sign_out")), reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class DashboardFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser("owner", "owner@example.com", "Test-only-password-529!")
        cls.python = TechStack.objects.create(name="Python")
        cls.django = TechStack.objects.create(name="Django")

    def setUp(self):
        self.client.force_login(self.owner)

    def data(self, **overrides):
        return {
            "project_name": "Portfolio manager", "description": "A" * 70,
            "tech_stacks_0": str(self.python.pk), "tech_stacks_1": str(self.django.pk),
            "link": "https://example.com/portfolio", **overrides,
        }

    def test_create_stack_records_name_date_and_shows_in_table(self):
        response = self.client.post(reverse("tech_stack_create"), {"name": "  Django   REST Framework  "})
        self.assertRedirects(response, reverse("dashboard_tech_stacks"))
        stack = TechStack.objects.get(name="Django REST Framework")
        self.assertIsNotNone(stack.created_at)
        response = self.client.get(reverse("dashboard_tech_stacks"))
        for text in (stack.name, "Not used yet", "Tech Stack Name", "Project It Was Used", "Date Added", "<time"):
            self.assertContains(response, text)

    def test_blank_and_duplicate_stack_names_fail_without_saving(self):
        for name in ("", "   ", "python", " PYTHON "):
            with self.subTest(name=name):
                response = self.client.post(reverse("tech_stack_create"), {"name": name})
                self.assertEqual(response.status_code, 200)
                self.assertIn("name", response.context["form"].errors)
        self.assertEqual(TechStack.objects.count(), 2)

    def test_database_prevents_case_insensitive_duplicate_stacks(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            TechStack.objects.create(name="PYTHON")

    def test_form_fetches_all_stacks_as_radio_options_and_uses_textarea(self):
        extra = TechStack.objects.create(name="PostgreSQL")
        response = self.client.get(reverse("dashboard_project_create"))
        self.assertContains(response, 'type="radio"', count=3)
        self.assertContains(response, extra.name)
        self.assertContains(response, f'value="{extra.pk}"')
        self.assertContains(response, '<textarea name="description"')
        self.assertContains(response, "+ Add another tech stack")

    def test_every_project_field_is_required(self):
        response = self.client.post(reverse("dashboard_project_create"), {})
        self.assertEqual(set(response.context["form"].errors), {"project_name", "description", "tech_stacks", "link"})
        self.assertEqual(Project.objects.count(), 0)

    def test_bad_urls_and_unknown_stack_ids_fail(self):
        for overrides in ({"link": "javascript:alert(1)"}, {"tech_stacks_0": "999999"}, {"tech_stacks_0": "not-an-id"}):
            with self.subTest(overrides=overrides):
                response = self.client.post(reverse("dashboard_project_create"), self.data(**overrides))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
        self.assertEqual(Project.objects.count(), 0)

    def test_invalid_post_keeps_text_and_selected_radio_groups(self):
        response = self.client.post(reverse("dashboard_project_create"), self.data(link="bad-url"))
        self.assertContains(response, 'value="Portfolio manager"')
        self.assertContains(response, ' checked required', count=2)
        self.assertContains(response, "Enter a valid URL.")

    def test_empty_toolkit_explains_what_to_do(self):
        TechStack.objects.all().delete()
        response = self.client.get(reverse("dashboard_project_create"))
        self.assertContains(response, "Create a tech stack before adding your first project.")
        self.assertContains(response, 'href="' + reverse("tech_stack_create") + '"')
        rejected = self.client.post(reverse("dashboard_project_create"), self.data())
        self.assertIn("tech_stacks", rejected.context["form"].errors)

    def test_projects_reuse_same_stack_objects_and_update_public_pages(self):
        for name in ("First project", "Second project"):
            response = self.client.post(reverse("dashboard_project_create"), self.data(project_name=name))
            self.assertRedirects(response, reverse("dashboard_projects"))
        self.assertEqual(TechStack.objects.count(), 2)
        self.assertEqual(self.python.projects.count(), 2)
        self.client.logout()
        for project in Project.objects.all():
            self.assertEqual(set(project.tech_stacks.all()), {self.python, self.django})
            for url in (reverse("home"), reverse("project_list"), reverse("project_detail", args=[project.pk])):
                response = self.client.get(url)
                for text in (project.project_name, "Python", "Django"):
                    self.assertContains(response, text)

    def test_dashboard_tables_show_required_columns_truncation_links_and_usage(self):
        self.client.post(reverse("dashboard_project_create"), self.data())
        project = Project.objects.get()
        response = self.client.get(reverse("dashboard_projects"))
        for label in ("Project Name", "Description", "Tech Stacks", "Link", "Django, Python"):
            self.assertContains(response, label)
        self.assertContains(response, Truncator(project.description).chars(50))
        self.assertNotContains(response, project.description)
        self.assertContains(response, 'href="' + project.link + '"')
        self.assertContains(response, reverse("dashboard_project_create"))
        stacks = self.client.get(reverse("dashboard_tech_stacks"))
        self.assertContains(stacks, project.project_name, count=2)
        self.assertContains(stacks, reverse("tech_stack_create"))


class LegacyTechStackMigrationTests(TransactionTestCase):
    old = [("website", "0002_inquiry_testimony")]
    new = [("website", "0003_reusable_tech_stacks")]

    def test_upgrade_preserves_projects_and_reuses_legacy_stacks(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.old)
        old_apps = executor.loader.project_state(self.old).apps
        OldProject = old_apps.get_model("website", "Project")
        first = OldProject.objects.create(project_name="Old project", description="Keep this", tech_stack="Python, Django, Python", link="https://example.com/one")
        second = OldProject.objects.create(project_name="Second", description="Also keep", tech_stack="python SQLite", link="https://example.com/two")
        try:
            executor = MigrationExecutor(connection)
            executor.migrate(self.new)
            apps = executor.loader.project_state(self.new).apps
            ProjectModel = apps.get_model("website", "Project")
            StackModel = apps.get_model("website", "TechStack")
            self.assertEqual(ProjectModel.objects.get(pk=first.pk).description, "Keep this")
            self.assertEqual(ProjectModel.objects.get(pk=second.pk).link, "https://example.com/two")
            self.assertEqual(set(ProjectModel.objects.get(pk=first.pk).tech_stacks.values_list("name", flat=True)), {"Python", "Django"})
            self.assertEqual(StackModel.objects.count(), 3)
            self.assertEqual(StackModel.objects.get(name="Python").projects.count(), 2)
        finally:
            MigrationExecutor(connection).migrate(self.new)
