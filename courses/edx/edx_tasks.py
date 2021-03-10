"""
edX Celery Tasks
Background tasks for edX course import operations.
"""

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .edx_production_importer import EdxProductionImporter
from .edx_test_importer import EdxTestImporter

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def import_edx_courses_task(self, max_pages=None, search_query=None, org_filter=None):
    """
    Celery task to import courses from edX.

    Args:
        max_pages (int): Maximum number of pages to import
        search_query (str): Search query to filter courses
        org_filter (str): Organization filter

    Returns:
        dict: Import statistics
    """
    logger.info("Starting edX course import task")

    try:
        importer = EdxProductionImporter()
        stats = importer.import_all_courses(
            max_pages=max_pages,
            search_query=search_query,
            org_filter=org_filter
        )

        # Send completion email
        _send_import_completion_email('edX', stats)

        logger.info("edX course import task completed successfully")
        return stats

    except Exception as e:
        logger.error(f"edX course import task failed: {e}")
        # Send failure email
        _send_import_failure_email('edX', str(e))
        raise


@shared_task(bind=True)
def import_edx_course_by_id_task(self, course_id):
    """
    Celery task to import a specific edX course by ID.

    Args:
        course_id (str): edX course ID

    Returns:
        dict: Import result
    """
    logger.info(f"Starting edX course import task for: {course_id}")

    try:
        importer = EdxProductionImporter()
        course = importer.import_course_by_id(course_id)

        result = {
            'success': course is not None,
            'course_id': course_id,
            'course_title': course.title if course else None
        }

        logger.info(f"edX course import task completed: {result}")
        return result

    except Exception as e:
        logger.error(f"edX course import task failed for {course_id}: {e}")
        raise


@shared_task(bind=True)
def import_edx_organization_task(self, organization, max_pages=None):
    """
    Celery task to import courses from a specific edX organization.

    Args:
        organization (str): Organization code (e.g., 'MITx', 'HarvardX')
        max_pages (int): Maximum number of pages to import

    Returns:
        dict: Import statistics
    """
    logger.info(f"Starting edX organization import task for: {organization}")

    try:
        importer = EdxProductionImporter()
        stats = importer.import_courses_by_organization(organization, max_pages)

        # Send completion email
        _send_import_completion_email(f'edX ({organization})', stats)

        logger.info(f"edX organization import task completed for: {organization}")
        return stats

    except Exception as e:
        logger.error(f"edX organization import task failed for {organization}: {e}")
        # Send failure email
        _send_import_failure_email(f'edX ({organization})', str(e))
        raise


@shared_task(bind=True)
def import_edx_test_courses_task(self):
    """
    Celery task to import edX test courses.

    Returns:
        dict: Import statistics
    """
    logger.info("Starting edX test courses import task")

    try:
        importer = EdxTestImporter()
        stats = importer.import_test_courses()

        logger.info("edX test courses import task completed successfully")
        return stats

    except Exception as e:
        logger.error(f"edX test courses import task failed: {e}")
        raise


@shared_task(bind=True)
def import_edx_sample_courses_task(self, limit=10):
    """
    Celery task to import edX sample courses.

    Args:
        limit (int): Number of courses to import

    Returns:
        dict: Import statistics
    """
    logger.info(f"Starting edX sample courses import task (limit: {limit})")

    try:
        importer = EdxTestImporter()
        stats = importer.import_sample_courses(limit)

        logger.info("edX sample courses import task completed successfully")
        return stats

    except Exception as e:
        logger.error(f"edX sample courses import task failed: {e}")
        raise


@shared_task(bind=True)
def cleanup_edx_test_courses_task(self):
    """
    Celery task to cleanup edX test courses.

    Returns:
        dict: Cleanup result
    """
    logger.info("Starting edX test courses cleanup task")

    try:
        importer = EdxTestImporter()
        deleted_count = importer.cleanup_test_courses()

        result = {
            'deleted_count': deleted_count,
            'success': True
        }

        logger.info(f"edX test courses cleanup task completed: {deleted_count} courses deleted")
        return result

    except Exception as e:
        logger.error(f"edX test courses cleanup task failed: {e}")
        raise


def _send_import_completion_email(platform, stats):
    """
    Send email notification when import is completed.

    Args:
        platform (str): Platform name
        stats (dict): Import statistics
    """
    if not settings.EMAIL_HOST_USER:
        logger.warning("Email not configured, skipping completion notification")
        return

    subject = f'{platform} Course Import Completed'
    message = f"""
    {platform} course import has been completed successfully.

    Import Statistics:
    - Processed: {stats.get('processed', 0)}
    - Created: {stats.get('created', 0)}
    - Updated: {stats.get('updated', 0)}
    - Errors: {stats.get('errors', 0)}
    - Skipped: {stats.get('skipped', 0)}

    Total courses in database: {stats.get('created', 0) + stats.get('updated', 0)}
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMINS[0][1] if settings.ADMINS else settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        logger.info(f"Import completion email sent for {platform}")
    except Exception as e:
        logger.error(f"Failed to send import completion email: {e}")


def _send_import_failure_email(platform, error_message):
    """
    Send email notification when import fails.

    Args:
        platform (str): Platform name
        error_message (str): Error message
    """
    if not settings.EMAIL_HOST_USER:
        logger.warning("Email not configured, skipping failure notification")
        return

    subject = f'{platform} Course Import Failed'
    message = f"""
    {platform} course import has failed.

    Error: {error_message}

    Please check the logs for more details.
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMINS[0][1] if settings.ADMINS else settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        logger.error(f"Import failure email sent for {platform}")
    except Exception as e:
        logger.error(f"Failed to send import failure email: {e}")


# Periodic task configurations for Celery Beat
EDX_IMPORT_SCHEDULE = {
    'task': 'courses.udemy.edx_tasks.import_edx_courses_task',
    'schedule': 604800.0,  # Run weekly (7 days * 24 hours * 60 minutes * 60 seconds)
    'args': (),
    'kwargs': {'max_pages': 50},  # Limit to 50 pages per weekly run
    'options': {'expires': 3600},  # Task expires in 1 hour
}

EDX_TEST_CLEANUP_SCHEDULE = {
    'task': 'courses.udemy.edx_tasks.cleanup_edx_test_courses_task',
    'schedule': 86400.0,  # Run daily (24 hours * 60 minutes * 60 seconds)
    'args': (),
    'kwargs': {},
    'options': {'expires': 3600},  # Task expires in 1 hour
}
