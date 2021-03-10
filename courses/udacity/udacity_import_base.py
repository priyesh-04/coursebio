"""
Udacity Course Importer Base
Base functionality for importing courses from Udacity JSON data.
"""

import logging
from datetime import datetime
from django.utils import timezone
from courses.models import Course, Provider, Category, SubCategory, Topic
from .udacity_data_loader import UdacityDataLoader

logger = logging.getLogger(__name__)


class UdacityImporterBase:
    """
    Base class for Udacity course importers.
    """

    def __init__(self, json_file_path=None):
        """
        Initialize Udacity importer.

        Args:
            json_file_path (str): Path to Udacity JSON file
        """
        self.data_loader = UdacityDataLoader(json_file_path)
        self.provider_name = 'Udacity'
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
        Get or create Udacity provider.

        Returns:
            Provider: Udacity provider instance
        """
        if not self.provider:
            self.provider, created = Provider.objects.get_or_create(
                name=self.provider_name,
                defaults={
                    'description': 'Udacity is an online learning platform offering courses from industry leaders and universities.',
                    'website': 'https://www.udacity.com',
                    'api_url': 'https://www.udacity.com/api/courses',  # Note: Not actually used
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
        Parse Udacity course data into standardized format.

        Args:
            course_data (dict): Raw course data from Udacity JSON

        Returns:
            dict: Standardized course data
        """
        try:
            # Extract basic course information
            course_key = course_data.get('key', '')
            if not course_key:
                logger.warning("Course data missing key")
                return None

            # Handle course title
            title = course_data.get('title', '').strip()
            if not title:
                logger.warning(f"Course {course_key} missing title")
                return None

            # Extract description and summary
            description = self.data_loader.get_course_summary(course_data) or ''
            short_description = course_data.get('short_summary', '')

            # Handle pricing information
            is_free = self.data_loader.is_free_course(course_data)
            price = 0.0 if is_free else 99.0  # Udacity courses are typically free or paid
            original_price = None
            discount_percentage = None

            # Extract duration
            duration = self.data_loader.parse_duration(course_data)

            # Extract language (default to English)
            language = 'English'

            # Extract enrollment information
            open_for_enrollment = course_data.get('open_for_enrollment', False)
            enrollment_start = None
            enrollment_end = None

            # Extract course dates
            launch_date = self.data_loader.parse_launch_date(course_data.get('launch_date'))
            course_start = launch_date
            course_end = None

            # Extract media URLs
            course_url = self.data_loader.get_course_url(
                course_key,
                course_data.get('slug')
            )
            image_url = self.data_loader.get_course_image_url(course_data)
            video_url = None  # Udacity doesn't typically provide direct video URLs

            # Extract instructor information
            instructor_names = self.data_loader.get_instructor_info(course_data)

            # Extract organization/school (Udacity itself)
            organization = 'Udacity'

            # Extract categories from tags
            tags = course_data.get('tags', [])
            categories = tags if tags else []

            # Extract level
            level = course_data.get('level', '')

            # Extract prerequisites
            required_knowledge = course_data.get('required_knowledge', '')
            prerequisites = [required_knowledge] if required_knowledge else []

            return {
                'course_key': course_key,
                'title': title,
                'description': description,
                'short_description': short_description,
                'price': price,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'duration': duration,
                'language': language,
                'enrollment_start': enrollment_start,
                'enrollment_end': enrollment_end,
                'course_start': course_start,
                'course_end': course_end,
                'course_url': course_url,
                'image_url': image_url,
                'video_url': video_url,
                'instructor_names': instructor_names,
                'organization': organization,
                'categories': categories,
                'level': level,
                'prerequisites': prerequisites,
                'raw_data': course_data,
                'is_available': course_data.get('available', False),
                'is_free': is_free
            }

        except Exception as e:
            logger.error(f"Error parsing course data for {course_data.get('key', 'unknown')}: {e}")
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
                'effort': course_data['duration'],  # Map duration to effort
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
                'is_active': course_data['is_available']
            }

            # Set free/paid status
            if course_data['is_free']:
                course_defaults['is_free'] = True
            else:
                course_defaults['price'] = course_data['price']

            # Try to get existing course or create new one
            course, created = Course.objects.get_or_create(
                course_id=course_data['course_key'],
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
            logger.error(f"Error creating/updating course {course_data.get('course_key', 'unknown')}: {e}")
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
        logger.info("Udacity Import Statistics:")
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
