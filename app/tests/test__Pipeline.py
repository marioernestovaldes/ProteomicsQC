from django.test import TestCase
from project.models import Project
from maxquant.models import Pipeline

from django.core.files.uploadedfile import SimpleUploadedFile


class PipelineTestCase(TestCase):
    def setUp(self):
        Project.objects.create(name="test-pipeline", description="a test project")
        project = Project.objects.get(name="test-pipeline")
        Pipeline.objects.create(name="test", project=project)

    def test__pipeline_creation(self):
        project = Project.objects.get(name="test-pipeline")
        pipeline = Pipeline.objects.get(name="test", project=project.pk)
        assert pipeline is not None, pipeline

    def test__pipeline_get_absolute_url_uses_current_maxquant_route(self):
        project = Project.objects.get(name="test-pipeline")
        pipeline = Pipeline.objects.get(name="test", project=project.pk)
        assert pipeline.get_absolute_url() == f"/proteomics/detail/{project.slug}/{pipeline.slug}"


class PipelineTestCaseWithFiles(TestCase):
    def setUp(self):
        Project.objects.create(name="project", description="a test project")
        project = Project.objects.get(name="project")

        contents_mqpar = b"""<?xml version="1.0" encoding="utf-8"?>
<MaxQuantParams xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
   <fastaFiles>
      <FastaFileInfo>
         <fastaFilePath>just testing</fastaFilePath>
      </FastaFileInfo>
   </fastaFiles>
   <filePaths>
      <string>example.raw</string>
   </filePaths>
   <experiments>
      <string>example-label</string>
   </experiments>
</MaxQuantParams>
"""
        contents_fasta = b">protein\nSEQUENCE"

        self.pipeline = Pipeline.objects.create(
            name="pipe",
            project=project,
            fasta_file=SimpleUploadedFile("my_fasta.fasta", contents_fasta),
            mqpar_file=SimpleUploadedFile("my_mqpar.xml", contents_mqpar),
        )

    def test__pipeline_mqpar_file_exists(self):
        assert self.pipeline.mqpar_path.is_file()

    def test__pipeline_fasta_file_exists(self):
        assert self.pipeline.fasta_path.is_file()

    def test__pipeline_has_maxquant_config(self):
        assert self.pipeline.has_maxquant_config

    def test__pipeline_mqpar_is_normalized_to_placeholders_on_save(self):
        content = self.pipeline.mqpar_path.read_text(encoding="utf-8")
        assert "__FASTA__" in content
        assert "__RAW__" in content
        assert "__LABEL__" in content
