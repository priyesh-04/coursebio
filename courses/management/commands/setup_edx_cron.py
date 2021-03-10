"""
Django management command for edX cron job setup.
Setup periodic tasks for edX course imports using Celery Beat.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from courses.edx.edx_tasks import (
    import_edx_courses_task,
    cleanup_edx_test_task
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for edX cron job setup operations.
    """

    help = 'Setup, remove, or list edX cron jobs using Celery Beat'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['setup', 'remove', 'list'],
            help='Action to perform: setup cron jobs, remove them, or list current jobs'
        )

    def handle(self, *args, **options):
        action = options['action']

        self.stdout.write(
            self.style.SUCCESS(f'Starting edX cron job {action} operation')
        )

        try:
            if action == 'setup':
                self.setup_edx_cron_jobs()
            elif action == 'remove':
                self.remove_edx_cron_jobs()
            elif action == 'list':
                self.list_edx_cron_jobs()

        except Exception as e:
            raise CommandError(f'edX cron job operation failed: {e}')

    def setup_edx_cron_jobs(self):
        """
        Setup periodic tasks for edX course imports.
        """
        self.stdout.write("Setting up edX cron jobs...")

        # Create interval schedules
        weekly_schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.WEEKS,
            defaults={'every': 1, 'period': IntervalSchedule.WEEKS}
        )
        if created:
            self.stdout.write("Created weekly schedule")

        daily_schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
            defaults={'every': 1, 'period': IntervalSchedule.DAYS}
        )
        if created:
            self.stdout.write("Created daily schedule")

        # Setup edX production import (weekly on Friday at midnight)
        edx_import_task, created = PeriodicTask.objects.get_or_create(
            name='Import edX Courses (Weekly)',
            task='courses.import_edx_courses',
            interval=weekly_schedule,
            defaults={
                'task': 'courses.import_edx_courses',
                'interval': weekly_schedule,
                'enabled': True,
                'kwargs': '{"max_pages": 50}',  # Limit to 50 pages per weekly run
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created edX weekly import task")
            )
        else:
            self.stdout.write("edX weekly import task already exists")

        # Setup edX test cleanup (daily)
        edx_cleanup_task, created = PeriodicTask.objects.get_or_create(
            name='Cleanup edX Test Courses (Daily)',
            task='courses.cleanup_edx_test',
            interval=daily_schedule,
            defaults={
                'task': 'courses.cleanup_edx_test',
                'interval': daily_schedule,
                'enabled': True,
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS("Created edX daily cleanup task")
            )
        else:
            self.stdout.write("edX daily cleanup task already exists")

        self.stdout.write(
            self.style.SUCCESS("edX cron jobs setup completed!")
        )

    def remove_edx_cron_jobs(self):
        """
        Remove edX periodic tasks.
        """
        self.stdout.write("Removing edX cron jobs...")

        # Remove edX tasks
        removed_count = PeriodicTask.objects.filter(
            task__in=[
                'courses.import_edx_courses',
                'courses.cleanup_edx_test'
            ]
        ).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(f'Removed {removed_count} edX cron jobs')
        )

    def list_edx_cron_jobs(self):
        """
        List all edX periodic tasks.
        """
        self.stdout.write("Current edX cron jobs:")

        edx_tasks = PeriodicTask.objects.filter(
            task__in=[
                'courses.import_edx_courses',
                'courses.cleanup_edx_test'
            ]
        )

        if not edx_tasks:
            self.stdout.write("No edX cron jobs found")
            return

        for task in edx_tasks:
            status = "enabled" if task.enabled else "disabled"
            self.stdout.write(f"- {task.name}: {task.task} ({status})")
