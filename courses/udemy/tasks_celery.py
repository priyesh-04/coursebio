"""
Celery tasks for Udemy and edX course import functionality.
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .udemy.importer import udemy_import_courses


@shared_task(bind=True, name='courses.import_udemy_courses')
def import_udemy_courses_task(self):
    """
    Celery task to import Udemy courses.
    This task runs the production Udemy course import process.
    """
    try:
        # Call the main Udemy import function
        result = udemy_import_courses()

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': 'Udemy course import completed successfully', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error and send notification
        error_message = f'Udemy import task failed: {str(exc)}'

        # Send error notification email
        try:
            from_email = settings.EMAIL_HOST_USER
            subject = 'Udemy Import Task Failed'
            message = f'The scheduled Udemy course import task failed with error: {str(exc)}'

            recipient1 = os.getenv('EMAIL_HOST_USER')
            recipient2 = os.getenv('MANAGER_EMAIL')
            recipient_list = [recipient1, recipient2]

            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=True
            )
        except Exception as email_exc:
            # Log email failure but don't raise
            print(f'Failed to send error notification email: {str(email_exc)}')

        # Update task state to FAILURE
        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        # Re-raise the exception to mark task as failed
        raise exc


@shared_task(bind=True, name='courses.test_udemy_import')
def test_udemy_import_task(self):
    """
    Celery task to test Udemy import functionality.
    This task runs the test Udemy course import process.
    """
    try:
        from .udemy.test_importer import udemy_import_test_course

        # Call the test Udemy import function
        result = udemy_import_test_course()

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': 'Test Udemy course import completed successfully', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error
        error_message = f'Test Udemy import task failed: {str(exc)}'

        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        raise exc


# edX Import Tasks

@shared_task(bind=True, name='courses.import_edx_courses')
def import_edx_courses_task(self, max_pages=None, search_query=None, org_filter=None):
    """
    Celery task to import edX courses.
    This task runs the production edX course import process.
    """
    try:
        from courses.edx.edx_production_importer import EdxProductionImporter

        importer = EdxProductionImporter()
        result = importer.import_all_courses(
            max_pages=max_pages,
            search_query=search_query,
            org_filter=org_filter
        )

        # Send completion email
        _send_import_completion_email('edX', result)

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': 'edX course import completed successfully', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error and send notification
        error_message = f'edX import task failed: {str(exc)}'

        # Send error notification email
        _send_import_failure_email('edX', error_message)

        # Update task state to FAILURE
        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        # Re-raise the exception to mark task as failed
        raise exc


@shared_task(bind=True, name='courses.import_edx_course_by_id')
def import_edx_course_by_id_task(self, course_id):
    """
    Celery task to import a specific edX course by ID.
    """
    try:
        from courses.edx.edx_production_importer import EdxProductionImporter

        importer = EdxProductionImporter()
        course = importer.import_course_by_id(course_id)

        result = {
            'success': course is not None,
            'course_id': course_id,
            'course_title': course.title if course else None
        }

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': f'edX course import completed: {course_id}', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error
        error_message = f'edX course import task failed for {course_id}: {str(exc)}'

        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        raise exc


@shared_task(bind=True, name='courses.import_edx_organization')
def import_edx_organization_task(self, organization, max_pages=None):
    """
    Celery task to import courses from a specific edX organization.
    """
    try:
        from courses.edx.edx_production_importer import EdxProductionImporter

        importer = EdxProductionImporter()
        result = importer.import_courses_by_organization(organization, max_pages)

        # Send completion email
        _send_import_completion_email(f'edX ({organization})', result)

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': f'edX organization import completed: {organization}', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error and send notification
        error_message = f'edX organization import task failed for {organization}: {str(exc)}'

        # Send error notification email
        _send_import_failure_email(f'edX ({organization})', error_message)

        # Update task state to FAILURE
        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        raise exc


@shared_task(bind=True, name='courses.test_edx_import')
def test_edx_import_task(self):
    """
    Celery task to test edX import functionality.
    """
    try:
        from courses.edx.edx_test_importer import EdxTestImporter

        importer = EdxTestImporter()
        result = importer.import_test_courses()

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': 'Test edX course import completed successfully', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error
        error_message = f'Test edX import task failed: {str(exc)}'

        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        raise exc


@shared_task(bind=True, name='courses.sample_edx_import')
def sample_edx_import_task(self, limit=10):
    """
    Celery task to import edX sample courses.
    """
    try:
        from courses.edx.edx_test_importer import EdxTestImporter

        importer = EdxTestImporter()
        result = importer.import_sample_courses(limit)

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': f'edX sample import completed: {limit} courses', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error
        error_message = f'edX sample import task failed: {str(exc)}'

        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        raise exc


@shared_task(bind=True, name='courses.cleanup_edx_test')
def cleanup_edx_test_task(self):
    """
    Celery task to cleanup edX test courses.
    """
    try:
        from courses.edx.edx_test_importer import EdxTestImporter

        importer = EdxTestImporter()
        deleted_count = importer.cleanup_test_courses()

        result = {
            'deleted_count': deleted_count,
            'success': True
        }

        # Log success
        self.update_state(
            state='SUCCESS',
            meta={'message': f'edX test cleanup completed: {deleted_count} courses deleted', 'result': result}
        )

        return result

    except Exception as exc:
        # Log error
        error_message = f'edX test cleanup task failed: {str(exc)}'

        self.update_state(
            state='FAILURE',
            meta={'message': error_message, 'exception': str(exc)}
        )

        raise exc


def _send_import_completion_email(platform, stats):
    """
    Send email notification when import is completed.

    Args:
        platform (str): Platform name
        stats (dict): Import statistics
    """
    if not settings.EMAIL_HOST_USER:
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
        from_email = settings.EMAIL_HOST_USER
        recipient1 = os.getenv('EMAIL_HOST_USER')
        recipient2 = os.getenv('MANAGER_EMAIL')
        recipient_list = [recipient1, recipient2]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True
        )
    except Exception as e:
        print(f'Failed to send completion email: {e}')


def _send_import_failure_email(platform, error_message):
    """
    Send email notification when import fails.

    Args:
        platform (str): Platform name
        error_message (str): Error message
    """
    if not settings.EMAIL_HOST_USER:
        return

    subject = f'{platform} Course Import Failed'
    message = f"""
    {platform} course import has failed.

    Error: {error_message}

    Please check the logs for more details.
    """

    try:
        from_email = settings.EMAIL_HOST_USER
        recipient1 = os.getenv('EMAIL_HOST_USER')
        recipient2 = os.getenv('MANAGER_EMAIL')
        recipient_list = [recipient1, recipient2]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True
        )
    except Exception as e:
        print(f'Failed to send failure email: {e}')
