from __future__ import absolute_import, unicode_literals
import logging
import os
from django.db import transaction

from .base import UdemyImportBase, BASE_CATEGORY_MAPPING
from courses.models import Course

# Configure logging
logger = logging.getLogger(__name__)


class UdemyTestImporter(UdemyImportBase):
    """
    Test/Development Udemy course importer.
    Handles import of specific test courses for development purposes.
    """

    def __init__(self, user_email=None):
        if user_email is None:
            user_email = os.getenv('DEFAULT_USER_EMAIL')
        super().__init__(
            category_mapping=BASE_CATEGORY_MAPPING,
            user_email=user_email
        )

    @transaction.atomic
    def import_test_course(self, course_id=269006, target_category='Development'):
        """
        Import a specific test course by ID.

        Args:
            course_id (int): Udemy course ID to import
            target_category (str): Category to assign the course to

        Returns:
            dict: Import statistics
        """
        logger.info(f"Starting test import for course ID: {course_id}")

        udemy_client = self.get_udemy_client()
        provider = self.get_provider()

        # Get initial course count
        initial_count = Course.objects.filter(provider__title='Udemy').count()
        logger.info(f"Initial course count: {initial_count}")

        courses_processed = 0
        courses_created = 0
        courses_updated = 0

        try:
            logger.info(f"Processing test course ID: {course_id}")
            course_detail = udemy_client.course_detail(course_id, course='@all')

            if course_detail:
                course_obj, created, updated = self.process_single_course(
                    course_detail, target_category
                )

                if course_obj:
                    courses_processed += 1
                    if created:
                        courses_created += 1
                    elif updated:
                        courses_updated += 1

        except Exception as e:
            logger.error(f"Error processing test course {course_id}: {str(e)}")

        # Final count
        final_count = Course.objects.filter(provider__title='Udemy').count()
        logger.info(f"Final course count: {final_count}")

        return {
            'initial_count': initial_count,
            'final_count': final_count,
            'courses_processed': courses_processed,
            'courses_created': courses_created,
            'courses_updated': courses_updated,
        }


# Global test importer instance
_test_importer = UdemyTestImporter()


@transaction.atomic
def udemy_import_test_course():
    """Main function to import Udemy courses - Test/Development version"""
    try:
        logger.info("Starting Udemy course import process (Test Version)")

        # Import test course
        stats = _test_importer.import_test_course(
            course_id=269006,
            target_category='Development'
        )

        # Send completion email
        if stats['initial_count'] == stats['final_count']:
            _test_importer.send_completion_email(
                'Test Udemy Import: All courses already exist',
                'No new courses were found to add to the database during test run.',
            )
        else:
            _test_importer.send_completion_email(
                'Test Udemy course import completed successfully',
                f'Test run completed. Processed {stats["courses_processed"]} courses. '
                f'Created: {stats["courses_created"]}, Updated: {stats["courses_updated"]}.',
            )

        logger.info("Udemy course import process (Test Version) completed successfully")
        return 'success'

    except Exception as e:
        logger.error(f"Udemy test import process failed: {str(e)}")
        _test_importer.send_completion_email(
            'Test Udemy course import failed',
            f'The test import process failed with error: {str(e)}',
        )
        raise


# Backward compatibility alias
udemy = udemy_import_test_course
