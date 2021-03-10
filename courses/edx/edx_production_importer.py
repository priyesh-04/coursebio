"""
edX Production Course Importer
Imports courses from edX platform for production use.
"""

import logging
import time
from django.core.management.base import BaseCommand
from .edx_import_base import EdxImporterBase

logger = logging.getLogger(__name__)


class EdxProductionImporter(EdxImporterBase):
    """
    Production importer for edX courses.
    Imports all available courses with proper error handling and rate limiting.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limit_delay = 1.0  # 1 second between requests
        self.max_retries = 3
        self.retry_delay = 5.0

    def import_all_courses(self, max_pages=None, search_query=None, org_filter=None):
        """
        Import all courses from edX.

        Args:
            max_pages (int): Maximum number of pages to import (None for all)
            search_query (str): Search query to filter courses
            org_filter (str): Organization filter

        Returns:
            dict: Import statistics
        """
        logger.info("Starting edX production import")
        self.reset_stats()

        page = 1
        total_imported = 0

        try:
            while True:
                if max_pages and page > max_pages:
                    logger.info(f"Reached maximum pages limit: {max_pages}")
                    break

                logger.info(f"Importing page {page}")

                try:
                    # Fetch courses from API
                    courses_data = self.api.courses(
                        page=page,
                        page_size=100,
                        search=search_query,
                        org=org_filter
                    )

                    # Check if we have results
                    results = courses_data.get('results', [])
                    if not results:
                        logger.info(f"No more courses found on page {page}")
                        break

                    # Process each course
                    for course_data in results:
                        self.stats['processed'] += 1

                        parsed_data = self.parse_course_data(course_data)
                        if parsed_data:
                            course, created = self.create_or_update_course(parsed_data)
                            if course:
                                total_imported += 1
                        else:
                            self.stats['skipped'] += 1

                    # Check pagination
                    next_page = courses_data.get('next')
                    if not next_page:
                        logger.info("No more pages available")
                        break

                    page += 1

                    # Rate limiting
                    if page % 10 == 0:  # Log progress every 10 pages
                        logger.info(f"Progress: {total_imported} courses imported so far")

                    time.sleep(self.rate_limit_delay)

                except Exception as e:
                    logger.error(f"Error importing page {page}: {e}")
                    self.stats['errors'] += 1

                    # Retry logic
                    if self._should_retry(page):
                        logger.info(f"Retrying page {page} after {self.retry_delay} seconds")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        logger.error(f"Max retries reached for page {page}, skipping")
                        break

            logger.info(f"edX production import completed. Total imported: {total_imported}")
            self.log_stats()

        except Exception as e:
            logger.error(f"Critical error during edX import: {e}")
            self.stats['errors'] += 1

        return self.stats

    def _should_retry(self, page):
        """
        Determine if we should retry a failed page.

        Args:
            page (int): Page number

        Returns:
            bool: Whether to retry
        """
        # Simple retry logic - could be enhanced with exponential backoff
        return page <= self.max_retries

    def import_course_by_id(self, course_id):
        """
        Import a specific course by its ID.

        Args:
            course_id (str): edX course ID

        Returns:
            Course: Imported course instance or None
        """
        logger.info(f"Importing specific edX course: {course_id}")

        try:
            # Get course details
            course_data = self.api.course_detail(course_id)

            if course_data:
                parsed_data = self.parse_course_data(course_data)
                if parsed_data:
                    course, created = self.create_or_update_course(parsed_data)
                    if course:
                        logger.info(f"Successfully imported course: {course.title}")
                        return course
                    else:
                        logger.error(f"Failed to create/update course: {course_id}")
                else:
                    logger.error(f"Failed to parse course data: {course_id}")
            else:
                logger.error(f"No course data found for: {course_id}")

        except Exception as e:
            logger.error(f"Error importing course {course_id}: {e}")
            self.stats['errors'] += 1

        return None

    def import_courses_by_organization(self, organization, max_pages=None):
        """
        Import courses from a specific organization.

        Args:
            organization (str): Organization code (e.g., 'MITx', 'HarvardX')
            max_pages (int): Maximum number of pages to import

        Returns:
            dict: Import statistics
        """
        logger.info(f"Importing edX courses from organization: {organization}")
        return self.import_all_courses(max_pages=max_pages, org_filter=organization)

    def import_courses_by_search(self, search_query, max_pages=None):
        """
        Import courses matching a search query.

        Args:
            search_query (str): Search query
            max_pages (int): Maximum number of pages to import

        Returns:
            dict: Import statistics
        """
        logger.info(f"Importing edX courses with search query: {search_query}")
        return self.import_all_courses(max_pages=max_pages, search_query=search_query)


class Command(BaseCommand):
    """
    Django management command for edX course import.
    """

    help = 'Import courses from edX platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-pages',
            type=int,
            help='Maximum number of pages to import',
        )
        parser.add_argument(
            '--search',
            type=str,
            help='Search query to filter courses',
        )
        parser.add_argument(
            '--org',
            type=str,
            help='Organization filter (e.g., MITx, HarvardX)',
        )
        parser.add_argument(
            '--course-id',
            type=str,
            help='Import specific course by ID',
        )

    def handle(self, *args, **options):
        importer = EdxProductionImporter()

        if options['course_id']:
            # Import specific course
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
            stats = importer.import_courses_by_organization(
                options['org'],
                options['max_pages']
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed: {stats["created"]} created, {stats["updated"]} updated'
                )
            )

        elif options['search']:
            # Import by search
            stats = importer.import_courses_by_search(
                options['search'],
                options['max_pages']
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed: {stats["created"]} created, {stats["updated"]} updated'
                )
            )

        else:
            # Import all courses
            stats = importer.import_all_courses(options['max_pages'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed: {stats["created"]} created, {stats["updated"]} updated'
                )
            )
