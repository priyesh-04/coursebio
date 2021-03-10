from __future__ import absolute_import, unicode_literals
import logging
from django.db import transaction

from .base import UdemyImportBase, PRODUCTION_CATEGORY_MAPPING
from courses.models import Course

# Configure logging
logger = logging.getLogger(__name__)


class UdemyProductionImporter(UdemyImportBase):
    """
    Production Udemy course importer.
    Handles bulk import of courses from multiple pages and categories.
    """

    def __init__(self):
        super().__init__(category_mapping=PRODUCTION_CATEGORY_MAPPING)

    @transaction.atomic
    def import_courses_by_category(self, target_category='Teaching+%26+Academics', max_pages=101):
        """
        Import courses from a specific Udemy category.

        Args:
            target_category (str): Udemy category to import from
            max_pages (int): Maximum number of pages to process

        Returns:
            dict: Import statistics
        """
        logger.info(f"Starting bulk import from category: {target_category}")

        udemy_client = self.get_udemy_client()
        provider = self.get_provider()
        local_category = self.get_or_create_category(target_category)

        # Get initial course count
        initial_count = Course.objects.filter(provider__title='Udemy').count()
        logger.info(f"Initial course count: {initial_count}")

        courses_processed = 0
        courses_created = 0
        courses_updated = 0

        # Process multiple pages
        for page in range(1, max_pages):
            try:
                logger.info(f"Processing page {page}")
                course_list = udemy_client.courses(
                    page=page,
                    page_size=100,
                    category=target_category
                )

                if not course_list.get('results'):
                    logger.info(f"No more courses found at page {page}")
                    break

                for course_data in course_list['results']:
                    try:
                        course_id = course_data['id']
                        course_detail = udemy_client.course_detail(course_id, course='@all')

                        if not course_detail:
                            continue

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
                        logger.error(f"Error processing course {course_data.get('id', 'unknown')}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error processing page {page}: {str(e)}")
                continue

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


# Global importer instance
_production_importer = UdemyProductionImporter()


@transaction.atomic
def udemy_import_courses():
    """Main function to import Udemy courses - Production version"""
    try:
        logger.info("Starting Udemy course import process")

        # Import courses from Teaching & Academics category
        stats = _production_importer.import_courses_by_category(
            target_category='Teaching+%26+Academics',
            max_pages=101
        )

        # Send completion email
        if stats['initial_count'] == stats['final_count']:
            _production_importer.send_completion_email(
                'All courses already exist in database',
                'No new courses were found to add to the database.',
            )
        else:
            _production_importer.send_completion_email(
                'Udemy course import completed successfully',
                f'Processed {stats["courses_processed"]} courses. '
                f'Created: {stats["courses_created"]}, Updated: {stats["courses_updated"]}.',
            )

        logger.info("Udemy course import process completed successfully")
        return 'success'

    except Exception as e:
        logger.error(f"Udemy import process failed: {str(e)}")
        _production_importer.send_completion_email(
            'Udemy course import failed',
            f'The import process failed with error: {str(e)}',
        )
        raise


# Backward compatibility alias
udemy = udemy_import_courses
