"""
Udacity Course Importer
Imports courses from Udacity JSON data.
"""

import logging
from django.core.management.base import BaseCommand
from .udacity_import_base import UdacityImporterBase

logger = logging.getLogger(__name__)


class UdacityImporter(UdacityImporterBase):
    """
    Production importer for Udacity courses.
    Imports courses from the JSON data file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def import_all_courses(self, only_available=True):
        """
        Import all courses from Udacity JSON data.

        Args:
            only_available (bool): Import only available courses

        Returns:
            dict: Import statistics
        """
        logger.info("Starting Udacity course import")
        self.reset_stats()

        try:
            # Get courses from data loader
            if only_available:
                courses_data = self.data_loader.get_available_courses()
                logger.info(f"Importing {len(courses_data)} available courses")
            else:
                courses_data = self.data_loader.get_all_courses()
                logger.info(f"Importing {len(courses_data)} total courses")

            # Process each course
            for course_data in courses_data:
                self.stats['processed'] += 1

                parsed_data = self.parse_course_data(course_data)
                if parsed_data:
                    course, created = self.create_or_update_course(parsed_data)
                    if not course:
                        self.stats['errors'] += 1
                else:
                    self.stats['skipped'] += 1
                    logger.warning(f"Failed to parse course data for: {course_data.get('key', 'unknown')}")

            logger.info("Udacity course import completed")
            self.log_stats()

        except Exception as e:
            logger.error(f"Critical error during Udacity import: {e}")
            self.stats['errors'] += 1

        return self.stats

    def import_course_by_key(self, course_key):
        """
        Import a specific course by its key.

        Args:
            course_key (str): Udacity course key

        Returns:
            Course: Imported course instance or None
        """
        logger.info(f"Importing specific Udacity course: {course_key}")

        try:
            # Get course data
            course_data = self.data_loader.get_course_by_key(course_key)

            if course_data:
                parsed_data = self.parse_course_data(course_data)
                if parsed_data:
                    course, created = self.create_or_update_course(parsed_data)
                    if course:
                        logger.info(f"Successfully imported course: {course.title}")
                        return course
                    else:
                        logger.error(f"Failed to create/update course: {course_key}")
                else:
                    logger.error(f"Failed to parse course data: {course_key}")
            else:
                logger.error(f"No course data found for: {course_key}")

        except Exception as e:
            logger.error(f"Error importing course {course_key}: {e}")
            self.stats['errors'] += 1

        return None

    def import_courses_by_level(self, level):
        """
        Import courses filtered by difficulty level.

        Args:
            level (str): Difficulty level (beginner, intermediate, advanced)

        Returns:
            dict: Import statistics
        """
        logger.info(f"Importing Udacity courses with level: {level}")
        self.reset_stats()

        try:
            # Get courses by level
            courses_data = self.data_loader.get_courses_by_level(level)
            logger.info(f"Found {len(courses_data)} courses with level: {level}")

            # Process each course
            for course_data in courses_data:
                self.stats['processed'] += 1

                parsed_data = self.parse_course_data(course_data)
                if parsed_data:
                    course, created = self.create_or_update_course(parsed_data)
                    if not course:
                        self.stats['errors'] += 1
                else:
                    self.stats['skipped'] += 1

            logger.info(f"Udacity level '{level}' import completed")
            self.log_stats()

        except Exception as e:
            logger.error(f"Error importing courses by level {level}: {e}")
            self.stats['errors'] += 1

        return self.stats

    def import_courses_by_tags(self, tags):
        """
        Import courses that match specified tags.

        Args:
            tags (list): List of tags to filter by

        Returns:
            dict: Import statistics
        """
        logger.info(f"Importing Udacity courses with tags: {tags}")
        self.reset_stats()

        try:
            # Get courses by tags
            courses_data = self.data_loader.get_courses_by_tags(tags)
            logger.info(f"Found {len(courses_data)} courses matching tags: {tags}")

            # Process each course
            for course_data in courses_data:
                self.stats['processed'] += 1

                parsed_data = self.parse_course_data(course_data)
                if parsed_data:
                    course, created = self.create_or_update_course(parsed_data)
                    if not course:
                        self.stats['errors'] += 1
                else:
                    self.stats['skipped'] += 1

            logger.info(f"Udacity tags '{tags}' import completed")
            self.log_stats()

        except Exception as e:
            logger.error(f"Error importing courses by tags {tags}: {e}")
            self.stats['errors'] += 1

        return self.stats


class Command(BaseCommand):
    """
    Django management command for Udacity course import.
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
