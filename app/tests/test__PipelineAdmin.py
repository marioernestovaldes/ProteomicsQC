from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from maxquant.models import Pipeline
from project.models import Project
from user.models import User


class PipelineAdminTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="pass1234"
        )

    def test_add_form_prefills_pipeline_defaults(self):
        Project.objects.create(
            name="Project 1",
            description="Existing project",
            created_by=self.admin_user,
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:maxquant_pipeline_add"))

        self.assertEqual(response.status_code, 200)
        form = response.context["adminform"].form

        self.assertIsNone(form.initial.get("project"))
        self.assertEqual(form.initial["name"], "Pipeline 1")
        self.assertEqual(form.initial["maxquant_executable"], settings.DEFAULT_MAXQUANT_EXECUTABLE)
        self.assertEqual(
            form.initial["description"],
            "Describe the pipeline purpose, processing settings, and sample scope.",
        )
        self.assertIn(
            (
                settings.DEFAULT_MAXQUANT_EXECUTABLE,
                "Bundled MaxQuant 2.4.12.0 (recommended)",
            ),
            list(form.fields["maxquant_executable"].choices),
        )
        self.assertIn("you must select the FASTA file again", form.fields["fasta_file"].help_text)

    def test_add_form_uses_next_available_pipeline_name(self):
        project = Project.objects.create(
            name="Project 1",
            description="Existing project",
            created_by=self.admin_user,
        )
        Pipeline.objects.create(
            name="Pipeline 1",
            description="Existing pipeline",
            project=project,
            created_by=self.admin_user,
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:maxquant_pipeline_add"))

        self.assertEqual(response.status_code, 200)
        form = response.context["adminform"].form
        self.assertEqual(form.initial["name"], "Pipeline 2")

    def test_add_form_hides_project_related_object_links(self):
        Project.objects.create(
            name="Project 1",
            description="Existing project",
            created_by=self.admin_user,
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:maxquant_pipeline_add"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "_addlink", html=False)
        self.assertNotContains(response, "_changelink", html=False)
        self.assertNotContains(response, "_deletelink", html=False)
        self.assertNotContains(response, "_viewlink", html=False)

    def test_add_form_requires_fasta_file_with_clear_error(self):
        project = Project.objects.create(
            name="Project 1",
            description="Existing project",
            created_by=self.admin_user,
        )

        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("admin:maxquant_pipeline_add"),
            data={
                "project": project.pk,
                "name": "Pipeline Missing Fasta",
                "description": "Test pipeline",
                "maxquant_executable": "/compute/software/MaxQuant/MaxQuant_v_2.4.12.0/bin/MaxQuantCmd.exe",
                "rawtools_args": "-q",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A FASTA file is required to create a runnable pipeline.", html=False)
