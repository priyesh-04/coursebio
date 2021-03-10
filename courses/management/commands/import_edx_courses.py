"""
Django management command for edX course import operations.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from courses.edx.edx_production_importer import EdxProductionImporter
from courses.edx.edx_test_importer import EdxTestImporter
from courses.edx.edx_tasks import (
    import_edx_courses_task,
    import_edx_course_by_id_task,
    import_edx_organization_task,
    import_edx_test_courses_task,
    import_edx_sample_courses_task,
    cleanup_edx_test_courses_task
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for edX course import operations.
    """

    help = 'Import courses from edX platform'

    def add_arguments(self, parser):
        # Import mode
        parser.add_argument(
            '--mode',
            choices=['production', 'test', 'sample', 'mock', 'cleanup'],
            default='production',
            help='Import mode (default: production)'
        )

        # Production import options
        parser.add_argument(
            '--max-pages',
            type=int,
            help='Maximum number of pages to import (production mode)'
        )
        parser.add_argument(
            '--search',
            type=str,
            help='Search query to filter courses (production mode)'
        )
        parser.add_argument(
            '--org',
            type=str,
            help='Organization filter (e.g., MITx, HarvardX) (production mode)'
        )
        parser.add_argument(
            '--course-id',
            type=str,
            help='Import specific course by ID (production mode)'
        )

        # Test/Sample import options
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of courses to import (sample mode, default: 10)'
        )

        # Async execution
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run import asynchronously using Celery'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        async_mode = options['async']

        self.stdout.write(
            self.style.SUCCESS(f'Starting edX import in {mode} mode{" (async)" if async_mode else ""}')
        )

        try:
            if mode == 'production':
                self._handle_production_import(options, async_mode)
            elif mode == 'test':
                self._handle_test_import(async_mode)
            elif mode == 'sample':
                self._handle_sample_import(options, async_mode)
            elif mode == 'mock':
                self._handle_mock_import()
            elif mode == 'cleanup':
                self._handle_cleanup(async_mode)

        except Exception as e:
            raise CommandError(f'edX import failed: {e}')

    def _handle_production_import(self, options, async_mode):
        """Handle production import mode."""
        if options['course_id']:
            # Import specific course
            if async_mode:
                task = import_edx_course_by_id_task.delay(options['course_id'])
                self.stdout.write(
                    self.style.SUCCESS(f'Async task started: {task.id}')
                )
            else:
                importer = EdxProductionImporter()
                course = importer.import_course_by_id(options['course_id'])
                if course:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully imported course: {course.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Failed to import course')
                    )

        elif options['org']:
            # Import by organization
            if async_mode:
                task = import_edx_organization_task.delay(
                    options['org'],
                    options['max_pages']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Async task started: {task.id}')
                )
            else:
                importer = EdxProductionImporter()
                stats = importer.import_courses_by_organization(
                    options['org'],
                    options['max_pages']
                )
                self._display_stats(stats)

        elif options['search']:
            # Import by search
            if async_mode:
                task = import_edx_courses_task.delay(
                    options['max_pages'],
                    options['search'],
                    None
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Async task started: {task.id}')
                )
            else:
                importer = EdxProductionImporter()
                stats = importer.import_courses_by_search(
                    options['search'],
                    options['max_pages']
                )
                self._display_stats(stats)

        else:
            # Import all courses
            if async_mode:
                task = import_edx_courses_task.delay(
                    options['max_pages'],
                    None,
                    None
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Async task started: {task.id}')
                )
            else:
                importer = EdxProductionImporter()
                stats = importer.import_all_courses(options['max_pages'])
                self._display_stats(stats)

    def _handle_test_import(self, async_mode):
        """Handle test import mode."""
        if async_mode:
            task = import_edx_test_courses_task.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Async test import task started: {task.id}')
            )
        else:
            importer = EdxTestImporter()
            stats = importer.import_test_courses()
            self._display_stats(stats)

    def _handle_sample_import(self, options, async_mode):
        """Handle sample import mode."""
        if async_mode:
            task = import_edx_sample_courses_task.delay(options['limit'])
            self.stdout.write(
                self.style.SUCCESS(f'Async sample import task started: {task.id}')
            )
        else:
            importer = EdxTestImporter()
            stats = importer.import_sample_courses(options['limit'])
            self._display_stats(stats)

    def _handle_mock_import(self):
        """Handle mock import mode."""
        importer = EdxTestImporter()
        stats = importer.import_mock_courses()
        self._display_stats(stats)

    def _handle_cleanup(self, async_mode):
        """Handle cleanup mode."""
        if async_mode:
            task = cleanup_edx_test_courses_task.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Async cleanup task started: {task.id}')
            )
        else:
            importer = EdxTestImporter()
            deleted_count = importer.cleanup_test_courses()
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {deleted_count} test courses')
            )

    def _display_stats(self, stats):
        """Display import statistics."""
        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed: {stats["created"]} created, {stats["updated"]} updated, '
                f'{stats["errors"]} errors, {stats["skipped"]} skipped'
            )
        )
        self.stdout.write(f'Processed: {stats["processed"]} courses')
