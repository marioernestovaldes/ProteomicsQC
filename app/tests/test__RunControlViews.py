from unittest.mock import PropertyMock, patch
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from maxquant.models import Pipeline, RawFile, Result
from project.models import Project
from user.models import User


class RunControlViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="run-control@example.com", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            email="run-control-other@example.com", password="pass1234"
        )
        self.project = Project.objects.create(
            name="Run Control Project",
            description="Run control tests",
            created_by=self.user,
        )
        self.project.users.add(self.user)
        self.pipeline = Pipeline.objects.create(
            name="run-control-pipe",
            project=self.project,
            created_by=self.user,
            fasta_file=SimpleUploadedFile("run-control.fasta", b">protein\nSEQUENCE"),
            mqpar_file=SimpleUploadedFile("run-control.xml", b"<mqpar></mqpar>"),
            rawtools_args="-p -q -x",
        )
        self.raw_file = RawFile.objects.create(
            pipeline=self.pipeline,
            orig_file=SimpleUploadedFile("owner.raw", b"..."),
            created_by=self.user,
        )
        self.result = Result.objects.get(raw_file=self.raw_file)

    def test_cancel_run_jobs_owner_can_cancel(self):
        self.client.force_login(self.user)
        with patch.object(Result, "cancel_active_jobs", return_value=3) as mock_cancel:
            response = self.client.post(
                reverse("maxquant:cancel_run_jobs", kwargs={"pk": self.result.pk})
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["revoked_tasks"], 3)
        mock_cancel.assert_called_once()

    def test_cancel_run_jobs_forbidden_for_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("maxquant:cancel_run_jobs", kwargs={"pk": self.result.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_cancel_pipeline_jobs_only_counts_active_runs(self):
        other_raw = RawFile.objects.create(
            pipeline=self.pipeline,
            orig_file=SimpleUploadedFile("owner-2.raw", b"..."),
            created_by=self.user,
        )
        Result.objects.get(raw_file=other_raw)
        self.client.force_login(self.user)

        with patch.object(Result, "has_active_stage", new_callable=PropertyMock, return_value=True):
            with patch.object(Result, "cancel_active_jobs", side_effect=[2, 1]) as mock_cancel:
                response = self.client.post(
                    reverse("maxquant:cancel_pipeline_jobs", kwargs={"pk": self.pipeline.pk})
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["runs_canceled"], 2)
        self.assertEqual(response.json()["revoked_tasks"], 3)
        self.assertEqual(mock_cancel.call_count, 2)

    def test_cancel_pipeline_jobs_forbidden_for_unrelated_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("maxquant:cancel_pipeline_jobs", kwargs={"pk": self.pipeline.pk})
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_raw_file_cancels_active_run_and_deletes_uuid_prefixed_upload(self):
        prefixed_raw = RawFile.objects.create(
            pipeline=self.pipeline,
            orig_file=SimpleUploadedFile("DeleteMe.RAW", b"..."),
            created_by=self.user,
        )
        RawFile.objects.filter(pk=prefixed_raw.pk).update(
            orig_file=f"upload/{uuid4().hex}_DeleteMe.RAW"
        )
        prefixed_raw.refresh_from_db()
        prefixed_result = Result.objects.get(raw_file=prefixed_raw)
        self.client.force_login(self.user)

        with patch.object(Result, "has_active_stage", new_callable=PropertyMock, return_value=True):
            with patch.object(Result, "cancel_active_jobs", return_value=4) as mock_cancel:
                response = self.client.post(
                    reverse("maxquant:delete_raw_file", kwargs={"pk": prefixed_raw.pk})
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["revoked_tasks"], 4)
        self.assertFalse(RawFile.objects.filter(pk=prefixed_raw.pk).exists())
        self.assertFalse(Result.objects.filter(pk=prefixed_result.pk).exists())
        mock_cancel.assert_called_once()

    def test_delete_raw_file_forbidden_for_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("maxquant:delete_raw_file", kwargs={"pk": self.raw_file.pk})
        )

        self.assertEqual(response.status_code, 404)
