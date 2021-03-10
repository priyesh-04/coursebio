"""
Django management command for Udacity course import operations.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from courses.udacity.udacity_importer import UdacityImporter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for Udacity course import operations.
    """

    help = 'Import courses from Udacity JSON data'

    def add_arguments(self, parser):
        # Import mode
        parser.add_argument(
            '--mode',
            choices=['all', 'available', 'level', 'tags', 'key'],
            default='available',
            help='Import mode (default: available)'
        )

        # Specific course import
        parser.add_argument(
            '--course-key',
            type=str,
            help='Import specific course by key (for --mode key)'
        )

        # Level filtering
        parser.add_argument(
            '--level',
            choices=['beginner', 'intermediate', 'advanced'],
            help='Filter by difficulty level (for --mode level)'
        )

        # Tag filtering
        parser.add_argument(
            '--tags',
            type=str,
            help='Comma-separated list of tags to filter by (for --mode tags)'
        )

    def handle(self, *args, **options):
        mode = options['mode']

        self.stdout.write(
            self.style.SUCCESS(f'Starting Udacity import in {mode} mode')
        )

        try:
            importer = UdacityImporter()

            if mode == 'key':
                # Import specific course
                if not options['course_key']:
                    self.stdout.write(
                        self.style.ERROR('--course-key is required for key mode')
                    )
                    return

                course = importer.import_course_by_key(options['course_key'])
                if course:
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully imported course: {course.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Failed to import course')
                    )

            elif mode == 'level':
                # Import by level
                if not options['level']:
                    self.stdout.write(
                        self.style.ERROR('--level is required for level mode')
                    )
                    return

                stats = importer.import_courses_by_level(options['level'])
                self._display_stats(stats)

            elif mode == 'tags':
                # Import by tags
                if not options['tags']:
                    self.stdout.write(
                        self.style.ERROR('--tags is required for tags mode')
                    )
                    return

                tags = [tag.strip() for tag in options['tags'].split(',')]
                stats = importer.import_courses_by_tags(tags)
                self._display_stats(stats)

            elif mode == 'all':
                # Import all courses
                stats = importer.import_all_courses(only_available=False)
                self._display_stats(stats)

            else:  # mode == 'available'
                # Import only available courses
                stats = importer.import_all_courses(only_available=True)
                self._display_stats(stats)

        except Exception as e:
            raise CommandError(f'Udacity import failed: {e}')

    def _display_stats(self, stats):
        """Display import statistics."""
        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed: {stats["created"]} created, {stats["updated"]} updated, '
                f'{stats["errors"]} errors, {stats["skipped"]} skipped'
            )
        )
        self.stdout.write(f'Processed: {stats["processed"]} courses')
