"""
edX Test Course Importer
Imports a limited set of courses from edX for testing purposes.
"""

import logging
import json
import os
from django.conf import settings
from .edx_import_base import EdxImporterBase

logger = logging.getLogger(__name__)


class EdxTestImporter(EdxImporterBase):
    """
    Test importer for edX courses.
    Imports a small, curated set of courses for testing and development.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_course_ids = [
            'MITx/6.00.1x/3T2019',  # Introduction to Computer Science and Programming Using Python
            'HarvardX/CS50x/2019',  # CS50's Introduction to Computer Science
            'MITx/6.0002x/3T2019',  # Introduction to Computational Thinking and Data Science
            'BerkeleyX/CS169.1x/2013_Spring',  # Software as a Service
            'AdelaideX/HumBio101x/1T2015',  # Human Biology: The Fundamentals
        ]

    def import_test_courses(self):
        """
        Import test courses from edX.

        Returns:
            dict: Import statistics
        """
        logger.info("Starting edX test import")
        self.reset_stats()

        for course_id in self.test_course_ids:
            logger.info(f"Importing test course: {course_id}")

            try:
                # Get course details
                course_data = self.api.course_detail(course_id)

                if course_data:
                    parsed_data = self.parse_course_data(course_data)
                    if parsed_data:
                        course, created = self.create_or_update_course(parsed_data)
                        if course:
                            logger.info(f"Successfully imported test course: {course.title}")
                        else:
                            logger.error(f"Failed to create/update test course: {course_id}")
                            self.stats['errors'] += 1
                    else:
                        logger.warning(f"Failed to parse test course data: {course_id}")
                        self.stats['skipped'] += 1
                else:
                    logger.warning(f"No data found for test course: {course_id}")
                    self.stats['skipped'] += 1

                self.stats['processed'] += 1

            except Exception as e:
                logger.error(f"Error importing test course {course_id}: {e}")
                self.stats['errors'] += 1

        logger.info("edX test import completed")
        self.log_stats()

        return self.stats

    def import_sample_courses(self, limit=10):
        """
        Import a sample of recent/popular courses for testing.

        Args:
            limit (int): Number of courses to import

        Returns:
            dict: Import statistics
        """
        logger.info(f"Starting edX sample import (limit: {limit})")
        self.reset_stats()

        try:
            # Get first page of courses
            courses_data = self.api.courses(page=1, page_size=limit)

            results = courses_data.get('results', [])
            if not results:
                logger.warning("No courses found in sample import")
                return self.stats

            # Process each course
            for course_data in results[:limit]:
                self.stats['processed'] += 1

                parsed_data = self.parse_course_data(course_data)
                if parsed_data:
                    course, created = self.create_or_update_course(parsed_data)
                    if course:
                        logger.info(f"Successfully imported sample course: {course.title}")
                    else:
                        logger.error(f"Failed to create/update sample course")
                        self.stats['errors'] += 1
                else:
                    logger.warning("Failed to parse sample course data")
                    self.stats['skipped'] += 1

        except Exception as e:
            logger.error(f"Error in sample import: {e}")
            self.stats['errors'] += 1

        logger.info("edX sample import completed")
        self.log_stats()

        return self.stats

    def create_mock_course_data(self):
        """
        Create mock course data for testing when API is not available.

        Returns:
            list: List of mock course data dictionaries
        """
        return [
            {
                'course_id': 'MITx/6.00.1x/3T2019',
                'name': 'Introduction to Computer Science and Programming Using Python',
                'description': 'This course is the first of a two-course sequence: Introduction to Computer Science and Programming Using Python, and Introduction to Computational Thinking and Data Science.',
                'short_description': 'Learn the fundamentals of programming in Python.',
                'org': 'MITx',
                'language': 'English',
                'effort': '10-15 hours/week',
                'level_type': 'Intermediate',
                'subjects': ['Computer Science'],
                'staff': [
                    {'given_name': 'John', 'family_name': 'Guttag'},
                    {'given_name': 'Eric', 'family_name': 'Grimson'}
                ],
                'start': '2019-09-05T00:00:00Z',
                'enrollment_start': '2019-08-01T00:00:00Z',
                'enrollment_end': '2019-12-31T23:59:59Z',
                'media': {
                    'course_image': {
                        'uri_absolute': 'https://prod-discovery.edx-cdn.org/media/course/image/6.00.1x-course_image.jpg'
                    }
                }
            },
            {
                'course_id': 'HarvardX/CS50x/2019',
                'name': 'CS50\'s Introduction to Computer Science',
                'description': 'This is CS50x, Harvard University\'s introduction to the intellectual enterprises of computer science and the art of programming.',
                'short_description': 'An introduction to the intellectual enterprises of computer science.',
                'org': 'HarvardX',
                'language': 'English',
                'effort': '6-18 hours/week',
                'level_type': 'Beginner',
                'subjects': ['Computer Science'],
                'staff': [
                    {'given_name': 'David', 'family_name': 'Malone'}
                ],
                'start': '2019-09-01T00:00:00Z',
                'enrollment_start': '2019-08-01T00:00:00Z',
                'media': {
                    'course_image': {
                        'uri_absolute': 'https://prod-discovery.edx-cdn.org/media/course/image/cs50x-course_image.jpg'
                    }
                }
            }
        ]

    def import_mock_courses(self):
        """
        Import mock courses for testing when API is not available.

        Returns:
            dict: Import statistics
        """
        logger.info("Starting edX mock import")
        self.reset_stats()

        mock_data = self.create_mock_course_data()

        for course_data in mock_data:
            self.stats['processed'] += 1

            parsed_data = self.parse_course_data(course_data)
            if parsed_data:
                course, created = self.create_or_update_course(parsed_data)
                if course:
                    logger.info(f"Successfully imported mock course: {course.title}")
                else:
                    logger.error("Failed to create/update mock course")
                    self.stats['errors'] += 1
            else:
                logger.warning("Failed to parse mock course data")
                self.stats['skipped'] += 1

        logger.info("edX mock import completed")
        self.log_stats()

        return self.stats

    def cleanup_test_courses(self):
        """
        Remove test courses from database.

        Returns:
            int: Number of courses removed
        """
        logger.info("Cleaning up edX test courses")

        provider = self.get_or_create_provider()
        test_course_ids = [course_id for course_id in self.test_course_ids]

        deleted_count = 0
        for course_id in test_course_ids:
            try:
                course = Course.objects.get(
                    course_id=course_id,
                    provider=provider
                )
                course.delete()
                deleted_count += 1
                logger.info(f"Deleted test course: {course.title}")
            except Course.DoesNotExist:
                logger.warning(f"Test course not found: {course_id}")
            except Exception as e:
                logger.error(f"Error deleting test course {course_id}: {e}")

        logger.info(f"Cleaned up {deleted_count} test courses")
        return deleted_count
