from django.core.management.base import BaseCommand, CommandError

from onboarding.bootstrap import (
    DEMO_PIPELINE_NAME,
    DEMO_PROJECT_NAME,
    bootstrap_demo_workspace,
)


class Command(BaseCommand):
    help = "Create or refresh a demo project and pipeline for onboarding."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            required=True,
            help="Email address of the user who should own the demo workspace.",
        )
        parser.add_argument(
            "--project-name",
            default=DEMO_PROJECT_NAME,
            help="Project name to create or reuse.",
        )
        parser.add_argument(
            "--pipeline-name",
            default=DEMO_PIPELINE_NAME,
            help="Pipeline name to create or reuse.",
        )
        parser.add_argument(
            "--with-results",
            action="store_true",
            help="Seed demo raw files and result artifacts so the UI is populated.",
        )
        parser.add_argument(
            "--password",
            default=None,
            help="Optional password to use if the target user needs to be created.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Refresh seeded demo raw files and results for the target user.",
        )

    def handle(self, *args, **options):
        try:
            bootstrap = bootstrap_demo_workspace(
                user_email=options["user"],
                project_name=options["project_name"],
                pipeline_name=options["pipeline_name"],
                with_results=options["with_results"],
                force=options["force"],
                user_password=options["password"],
            )
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("Demo workspace ready."))
        self.stdout.write("")
        self.stdout.write(f"User: {bootstrap.user.email}")
        self.stdout.write(f"Created user: {'yes' if bootstrap.created_user else 'no'}")
        if bootstrap.generated_password:
            self.stdout.write(f"Temporary password: {bootstrap.generated_password}")
        self.stdout.write(f"Project: {bootstrap.project.name}")
        self.stdout.write(f"Pipeline: {bootstrap.pipeline.name}")
        self.stdout.write(
            f"Created project: {'yes' if bootstrap.created_project else 'no'}"
        )
        self.stdout.write(
            f"Created pipeline: {'yes' if bootstrap.created_pipeline else 'no'}"
        )
        self.stdout.write(f"Seeded raw files: {len(bootstrap.raw_files)}")
        self.stdout.write(f"Seeded results: {len(bootstrap.results)}")
        self.stdout.write("")
        self.stdout.write("Admin:")
        self.stdout.write("  /admin/project/project/")
        self.stdout.write("  /admin/maxquant/pipeline/")
        self.stdout.write("  /admin/maxquant/rawfile/")
        self.stdout.write("  /admin/maxquant/result/")
        self.stdout.write("")
        self.stdout.write("App:")
        self.stdout.write(f"  {bootstrap.project.url}")
        self.stdout.write(f"  {bootstrap.pipeline.url}")
        self.stdout.write("  /dashboard/")
