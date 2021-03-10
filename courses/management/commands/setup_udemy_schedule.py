"""
Management command to set up periodic Udemy import tasks.
This command creates or updates the Celery Beat periodic task
that runs Udemy course import every Friday at 12:00 AM.
"""

from django.core.management.base import BaseCommand, CommandError
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


class Command(BaseCommand):
    help = 'Set up periodic Udemy course import task to run every Friday at 12:00 AM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Set up test import task instead of production import',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up Udemy import periodic task...')
        )

        # Define task details based on whether it's test or production
        if options['test']:
            task_name = 'Test Udemy Course Import'
            task_description = 'Test Udemy course import (single course)'
            task_function = 'courses.udemy.tasks_celery.test_udemy_import_task'
            cron_minute = '0'
            cron_hour = '0'
            cron_day_of_week = '5'  # Friday
            cron_day_of_month = '*'
            cron_month_of_year = '*'
        else:
            task_name = 'Production Udemy Course Import'
            task_description = 'Production Udemy course import (bulk import)'
            task_function = 'courses.udemy.tasks_celery.import_udemy_courses_task'
            cron_minute = '0'
            cron_hour = '0'
            cron_day_of_week = '5'  # Friday
            cron_day_of_month = '*'
            cron_month_of_year = '*'

        try:
            # Create or get the crontab schedule for Friday at midnight
            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=cron_minute,
                hour=cron_hour,
                day_of_week=cron_day_of_week,
                day_of_month=cron_day_of_month,
                month_of_year=cron_month_of_year,
                timezone='UTC'
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created crontab schedule: {schedule}')
                )

            # Create or update the periodic task
            task, created = PeriodicTask.objects.get_or_create(
                name=task_name,
                defaults={
                    'task': task_function,
                    'crontab': schedule,
                    'enabled': True,
                    'description': task_description,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created periodic task: {task_name}')
                )
            else:
                # Update existing task
                task.task = task_function
                task.crontab = schedule
                task.enabled = True
                task.description = task_description
                task.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Updated existing periodic task: {task_name}')
                )

            # Display task details
            self.stdout.write(
                self.style.SUCCESS(f'\nTask Details:')
            )
            self.stdout.write(f'  Name: {task.name}')
            self.stdout.write(f'  Task: {task.task}')
            self.stdout.write(f'  Schedule: Every Friday at 12:00 AM UTC')
            self.stdout.write(f'  Enabled: {task.enabled}')
            self.stdout.write(f'  Description: {task.description}')

            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Udemy import periodic task setup completed!')
            )

        except Exception as e:
            raise CommandError(f'Failed to set up periodic task: {str(e)}')
