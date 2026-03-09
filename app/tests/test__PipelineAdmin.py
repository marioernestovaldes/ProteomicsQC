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
        self.contents_fasta = b">sp|P00001|TEST_PROTEIN Test protein\nMPEPTIDESEQ\n"
        self.contents_mqpar = (
            b'<?xml version="1.0" encoding="utf-8"?>\n'
            b"<MaxQuantParams>\n"
            b"  <fastaFiles>\n"
            b"    <FastaFileInfo>\n"
            b"      <fastaFilePath>example.fasta</fastaFilePath>\n"
            b"    </FastaFileInfo>\n"
            b"  </fastaFiles>\n"
            b"  <filePaths>\n"
            b"    <string>sample.raw</string>\n"
            b"  </filePaths>\n"
            b"  <experiments>\n"
            b"    <string>Sample 1</string>\n"
            b"  </experiments>\n"
            b"</MaxQuantParams>\n"
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

    def test_add_form_rejects_fasta_file_uploaded_as_mqpar(self):
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
                "name": "Pipeline Swapped MQPAR",
                "description": "Test pipeline",
                "maxquant_executable": settings.DEFAULT_MAXQUANT_EXECUTABLE,
                "rawtools_args": "-q",
                "fasta_file": SimpleUploadedFile("proteins.fasta", self.contents_fasta),
                "mqpar_file": SimpleUploadedFile("wrong.xml", self.contents_fasta),
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "MQPAR upload warning: this file looks like a FASTA file, not an mqpar.xml file.",
            html=False,
        )
        self.assertTrue(Pipeline.objects.filter(name="Pipeline Swapped MQPAR").exists())

    def test_add_form_rejects_mqpar_file_uploaded_as_fasta(self):
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
                "name": "Pipeline Swapped FASTA",
                "description": "Test pipeline",
                "maxquant_executable": settings.DEFAULT_MAXQUANT_EXECUTABLE,
                "rawtools_args": "-q",
                "fasta_file": SimpleUploadedFile("wrong.fasta", self.contents_mqpar),
                "mqpar_file": SimpleUploadedFile("params.xml", self.contents_mqpar),
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "FASTA upload warning: this file looks like an mqpar.xml file, not a FASTA file.",
            html=False,
        )
        self.assertTrue(Pipeline.objects.filter(name="Pipeline Swapped FASTA").exists())

    def test_add_form_rejects_non_fasta_uploads_for_fasta_field(self):
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
                "name": "Pipeline Invalid FASTA",
                "description": "Test pipeline",
                "maxquant_executable": settings.DEFAULT_MAXQUANT_EXECUTABLE,
                "rawtools_args": "-q",
                "fasta_file": SimpleUploadedFile("invalid.fasta", b"not a fasta file"),
                "mqpar_file": SimpleUploadedFile("params.xml", self.contents_mqpar),
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "FASTA upload warning: this file does not look like a FASTA file.",
            html=False,
        )
        self.assertTrue(Pipeline.objects.filter(name="Pipeline Invalid FASTA").exists())

    def test_add_form_rejects_non_mqpar_uploads_for_mqpar_field(self):
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
                "name": "Pipeline Invalid MQPAR",
                "description": "Test pipeline",
                "maxquant_executable": settings.DEFAULT_MAXQUANT_EXECUTABLE,
                "rawtools_args": "-q",
                "fasta_file": SimpleUploadedFile("proteins.fasta", self.contents_fasta),
                "mqpar_file": SimpleUploadedFile("invalid.xml", b"plain text"),
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "MQPAR upload warning: this file does not look like a valid mqpar.xml file.",
            html=False,
        )
        self.assertTrue(Pipeline.objects.filter(name="Pipeline Invalid MQPAR").exists())

    def test_change_form_shows_warning_for_existing_suspicious_files(self):
        project = Project.objects.create(
            name="Project 1",
            description="Existing project",
            created_by=self.admin_user,
        )
        pipeline = Pipeline.objects.create(
            name="Pipeline Existing Warning",
            description="Test pipeline",
            project=project,
            created_by=self.admin_user,
            fasta_file=SimpleUploadedFile("wrong.fasta", self.contents_mqpar),
            mqpar_file=SimpleUploadedFile("params.xml", self.contents_mqpar),
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:maxquant_pipeline_change", args=[pipeline.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "FASTA upload warning: this file looks like an mqpar.xml file, not a FASTA file.",
            html=False,
        )
