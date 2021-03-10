"""
edX Course Importer Base
Base functionality for importing courses from edX platform.
"""

import logging
from datetime import datetime
from django.utils import timezone
from courses.models import Course, Provider, Category, SubCategory, Topic
from .edx import EdxAPI

logger = logging.getLogger(__name__)


class EdxImporterBase:
    """
    Base class for edX course importers.
    """

    def __init__(self, client_id=None, client_secret=None, base_url=None):
        """
        Initialize edX importer.

        Args:
            client_id (str): edX API client ID
            client_secret (str): edX API client secret
            base_url (str): Base URL for edX API
        """
        self.api = EdxAPI(client_id, client_secret, base_url)
        self.provider_name = 'edX'
        self.provider = None
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }

    def get_or_create_provider(self):
        """
        Get or create edX provider.

        Returns:
            Provider: edX provider instance
        """
        if not self.provider:
            self.provider, created = Provider.objects.get_or_create(
                name=self.provider_name,
                defaults={
                    'description': 'edX is an online learning platform offering courses from universities and institutions worldwide.',
                    'website': 'https://www.edx.org',
                    'api_url': 'https://courses.edx.org/api',
                    'is_active': True
                }
            )
            if created:
                logger.info(f"Created new provider: {self.provider_name}")
            else:
                logger.info(f"Using existing provider: {self.provider_name}")

        return self.provider

    def parse_course_data(self, course_data):
        """
        Parse edX course data into standardized format.

        Args:
            course_data (dict): Raw course data from edX API

        Returns:
            dict: Standardized course data
        """
        try:
            # Extract basic course information
            course_id = course_data.get('course_id', course_data.get('id', ''))
            if not course_id:
                logger.warning("Course data missing ID")
                return None

            # Handle course title
            title = course_data.get('name', course_data.get('title', ''))
            if not title:
                logger.warning(f"Course {course_id} missing title")
                return None

            # Extract description
            description = course_data.get('description', '')
            short_description = course_data.get('short_description', '')

            # Handle pricing information
            price = 0.0  # edX courses are generally free
            original_price = None
            discount_percentage = None

            # Extract duration/effort information
            effort = course_data.get('effort')
            if effort:
                effort = self.api.parse_effort(effort)

            # Extract language
            language = course_data.get('language', 'English')

            # Extract enrollment information
            enrollment_start = course_data.get('enrollment_start')
            enrollment_end = course_data.get('enrollment_end')
            course_start = course_data.get('start')
            course_end = course_data.get('end')

            # Parse dates
            enrollment_start_date = None
            enrollment_end_date = None
            course_start_date = None
            course_end_date = None

            try:
                if enrollment_start:
                    enrollment_start_date = datetime.fromisoformat(enrollment_start.replace('Z', '+00:00'))
                if enrollment_end:
                    enrollment_end_date = datetime.fromisoformat(enrollment_end.replace('Z', '+00:00'))
                if course_start:
                    course_start_date = datetime.fromisoformat(course_start.replace('Z', '+00:00'))
                if course_end:
                    course_end_date = datetime.fromisoformat(course_end.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error parsing dates for course {course_id}: {e}")

            # Extract media URLs
            course_url = self.api.get_course_url(course_id)
            image_url = self.api.get_course_image_url(course_data)
            video_url = self.api.get_course_video_url(course_data)

            # Extract instructor information
            instructors = course_data.get('staff', [])
            instructor_names = []
            if instructors:
                for instructor in instructors:
                    if isinstance(instructor, dict):
                        name = instructor.get('given_name', '') + ' ' + instructor.get('family_name', '')
                        name = name.strip()
                        if name:
                            instructor_names.append(name)
                    elif isinstance(instructor, str):
                        instructor_names.append(instructor)

            # Extract organization/institution
            org = course_data.get('org', course_data.get('organization', ''))
            if not org and course_id:
                # Try to extract from course_id (format: org+course+run)
                parts = course_id.split('+')
                if len(parts) >= 1:
                    org = parts[0]

            # Extract subject/categories
            subjects = course_data.get('subjects', [])
            if isinstance(subjects, list):
                categories = subjects
            else:
                categories = []

            # Extract level
            level = course_data.get('level_type', course_data.get('level', ''))

            # Extract prerequisites
            prerequisites = course_data.get('prerequisites', [])

            return {
                'course_id': course_id,
                'title': title,
                'description': description,
                'short_description': short_description,
                'price': price,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'effort': effort,
                'language': language,
                'enrollment_start': enrollment_start_date,
                'enrollment_end': enrollment_end_date,
                'course_start': course_start_date,
                'course_end': course_end_date,
                'course_url': course_url,
                'image_url': image_url,
                'video_url': video_url,
                'instructor_names': instructor_names,
                'organization': org,
                'categories': categories,
                'level': level,
                'prerequisites': prerequisites,
                'raw_data': course_data
            }

        except Exception as e:
            logger.error(f"Error parsing course data: {e}")
            return None

    def get_or_create_category(self, category_name):
        """
        Get or create category.

        Args:
            category_name (str): Category name

        Returns:
            Category: Category instance
        """
        if not category_name:
            return None

        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={'description': f'Courses related to {category_name}'}
        )
        return category

    def get_or_create_subcategory(self, subcategory_name, category):
        """
        Get or create subcategory.

        Args:
            subcategory_name (str): Subcategory name
            category (Category): Parent category

        Returns:
            SubCategory: SubCategory instance
        """
        if not subcategory_name or not category:
            return None

        subcategory, created = SubCategory.objects.get_or_create(
            name=subcategory_name,
            category=category,
            defaults={'description': f'Subcategory of {category.name}'}
        )
        return subcategory

    def get_or_create_topic(self, topic_name, subcategory):
        """
        Get or create topic.

        Args:
            topic_name (str): Topic name
            subcategory (SubCategory): Parent subcategory

        Returns:
            Topic: Topic instance
        """
        if not topic_name or not subcategory:
            return None

        topic, created = Topic.objects.get_or_create(
            name=topic_name,
            subcategory=subcategory,
            defaults={'description': f'Topic under {subcategory.name}'}
        )
        return topic

    def create_or_update_course(self, course_data):
        """
        Create or update course in database.

        Args:
            course_data (dict): Parsed course data

        Returns:
            tuple: (Course instance, created boolean)
        """
        try:
            provider = self.get_or_create_provider()

            # Create course data for model
            course_defaults = {
                'title': course_data['title'],
                'description': course_data['description'],
                'short_description': course_data['short_description'],
                'price': course_data['price'],
                'original_price': course_data['original_price'],
                'discount_percentage': course_data['discount_percentage'],
                'effort': course_data['effort'],
                'language': course_data['language'],
                'enrollment_start': course_data['enrollment_start'],
                'enrollment_end': course_data['enrollment_end'],
                'course_start': course_data['course_start'],
                'course_end': course_data['course_end'],
                'course_url': course_data['course_url'],
                'image_url': course_data['image_url'],
                'video_url': course_data['video_url'],
                'instructor_names': course_data['instructor_names'],
                'organization': course_data['organization'],
                'level': course_data['level'],
                'prerequisites': course_data['prerequisites'],
                'raw_data': course_data['raw_data'],
                'last_updated': timezone.now(),
                'is_active': True
            }

            # Try to get existing course or create new one
            course, created = Course.objects.get_or_create(
                course_id=course_data['course_id'],
                provider=provider,
                defaults=course_defaults
            )

            if not created:
                # Update existing course
                for key, value in course_defaults.items():
                    setattr(course, key, value)
                course.save()
                logger.info(f"Updated course: {course.title}")
                self.stats['updated'] += 1
            else:
                logger.info(f"Created course: {course.title}")
                self.stats['created'] += 1

            # Handle categories and topics
            self._handle_course_categories(course, course_data['categories'])

            return course, created

        except Exception as e:
            logger.error(f"Error creating/updating course {course_data.get('course_id', 'unknown')}: {e}")
            self.stats['errors'] += 1
            return None, False

    def _handle_course_categories(self, course, categories):
        """
        Handle course categories, subcategories, and topics.

        Args:
            course (Course): Course instance
            categories (list): List of category names
        """
        if not categories:
            return

        # Clear existing relationships
        course.categories.clear()
        course.subcategories.clear()
        course.topics.clear()

        for category_name in categories:
            if not category_name:
                continue

            # Create category
            category = self.get_or_create_category(category_name)
            if category:
                course.categories.add(category)

                # For now, we'll treat categories as both categories and subcategories
                # In a more complex implementation, you might want to parse hierarchical data
                subcategory = self.get_or_create_subcategory(category_name, category)
                if subcategory:
                    course.subcategories.add(subcategory)

                    # Create topic with same name
                    topic = self.get_or_create_topic(category_name, subcategory)
                    if topic:
                        course.topics.add(topic)

    def log_stats(self):
        """
        Log import statistics.
        """
        logger.info("edX Import Statistics:")
        logger.info(f"  Processed: {self.stats['processed']}")
        logger.info(f"  Created: {self.stats['created']}")
        logger.info(f"  Updated: {self.stats['updated']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info(f"  Skipped: {self.stats['skipped']}")

    def reset_stats(self):
        """
        Reset import statistics.
        """
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }
