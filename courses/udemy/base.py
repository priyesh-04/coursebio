"""
Shared utilities for Udemy course import functionality.
This module contains common functions and configurations used by both
production and test Udemy import tasks.
"""

from __future__ import absolute_import, unicode_literals
import os
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

import importlib.util
import os

# Import Udemy class from the parent directory's udemy.py file
udemy_spec = importlib.util.spec_from_file_location("udemy_module", os.path.join(os.path.dirname(os.path.dirname(__file__)), "udemy.py"))
udemy_module = importlib.util.module_from_spec(udemy_spec)
udemy_spec.loader.exec_module(udemy_module)
Udemy = udemy_module.Udemy
from accounts.models import MyUser
from courses.models import Category, SubCategory, Provider, Course, Topic

# Configure logging
logger = logging.getLogger(__name__)

# Udemy API Configuration
UDEMY_CLIENT_ID = os.getenv('UDEMY_CLIENT_ID')
UDEMY_CLIENT_SECRET = os.getenv('UDEMY_CLIENT_SECRET')

# Base category mapping for Udemy to local categories
BASE_CATEGORY_MAPPING = {
    'Development': 'Computer Science',
    'Design': 'Arts & Design',
    'Business': 'Business',
    'Finance+%26+Accounting': 'Finance & Accounting',
    'Health+%26+Fitness': 'Health & Fitness',
    'IT+%26+Software': 'IT & Software',
    'Lifestyle': 'Lifestyle',
    'Marketing': 'Marketing',
    'Music': 'Music',
    'Office Productivity': 'Office Productivity',
    'Personal Development': 'Personal Development',
    'Photography': 'Photography',
    'Teaching+%26+Academics': 'Teaching & Academics',
}

# Extended category mapping for production use
PRODUCTION_CATEGORY_MAPPING = {
    **BASE_CATEGORY_MAPPING,
    'IT+%26+Software': 'IT & Computer Science',
    'Lifestyle': 'Professions & Hobbies',
    'Photography': 'Arts & Design',
    'Photography+%26+Video': 'Arts & Design',
}


class UdemyImportBase:
    """
    Base class for Udemy course import functionality.
    Contains common methods and configurations shared between
    production and test import tasks.
    """

    def __init__(self, category_mapping=None, user_email=None):
        """
        Initialize the Udemy import handler.

        Args:
            category_mapping (dict): Mapping from Udemy categories to local categories
            user_email (str): Specific user email to use for course assignment (optional)
        """
        self.category_mapping = category_mapping or BASE_CATEGORY_MAPPING
        self.user_email = user_email
        self.udemy_client = None
        self.provider = None

    def get_udemy_client(self):
        """Initialize and return Udemy API client"""
        if not UDEMY_CLIENT_ID or not UDEMY_CLIENT_SECRET:
            raise ValueError("Udemy API credentials not found in environment variables")

        if self.udemy_client is None:
            self.udemy_client = Udemy(UDEMY_CLIENT_ID, UDEMY_CLIENT_SECRET)

        return self.udemy_client

    def get_provider(self):
        """Get or create Udemy provider"""
        if self.provider is None:
            try:
                self.provider = Provider.objects.get(title='Udemy')
            except Provider.DoesNotExist:
                logger.error("Udemy provider not found in database")
                raise
        return self.provider

    def get_user(self):
        """Get user for course assignment"""
        if self.user_email:
            try:
                return MyUser.objects.get(email=self.user_email)
            except MyUser.DoesNotExist:
                logger.error(f"Specified user not found: {self.user_email}")
                raise
        else:
            # Use any superuser for production
            user = MyUser.objects.filter(is_superuser=True).first()
            if not user:
                logger.error("No superuser found to assign courses to")
                raise ValueError("No superuser found")
            return user

    def get_or_create_category(self, udemy_category):
        """Get or create local category from Udemy category"""
        local_category_name = self.category_mapping.get(udemy_category, udemy_category)
        category, created = Category.objects.get_or_create(
            title=local_category_name,
            defaults={'slug': local_category_name.lower().replace(' ', '-')}
        )
        return category

    def update_course_details(self, course_obj, course_detail):
        """Update course with detailed information from Udemy API"""
        try:
            # Update subscriber count and popularity
            num_subscribers = course_detail.get('num_subscribers')
            if num_subscribers:
                course_obj.num_subscribers = num_subscribers
                course_obj.is_popular = num_subscribers > 5000

            # Update rating information
            rating = course_detail.get('avg_rating')
            num_reviews = course_detail.get('num_reviews')
            if rating:
                course_obj.rating = rating
            if num_reviews:
                course_obj.num_reviews = num_reviews

            # Update video URL if available
            try:
                video_url = course_detail['promo_asset']['download_urls']['Video'][0]['file']
                course_obj.video_url = video_url
            except (KeyError, IndexError):
                logger.info(f"No video available for course: {course_obj.title}")

            course_obj.save()
            logger.info(f"Updated course details for: {course_obj.title}")

        except Exception as e:
            logger.error(f"Error updating course details for {course_obj.title}: {str(e)}")

    def create_course_description(self, course_detail):
        """Create comprehensive course description from Udemy data"""
        description = ""

        # Add "What you'll learn" section
        try:
            what_youll_learn = course_detail['what_you_will_learn_data']['items']
            if what_youll_learn:
                description += "<h3><strong>What you'll learn:</strong></h3><ol>"
                for item in what_youll_learn:
                    description += f"<li>{item}</li>"
                description += "</ol><hr>"
        except (KeyError, TypeError):
            logger.warning("No 'what you'll learn' data available")

        # Add course description
        try:
            course_description = course_detail.get('description', '')
            if course_description:
                description += "<h3><strong>About this course:</strong></h3>"
                description += course_description
        except Exception as e:
            logger.error(f"Error processing course description: {str(e)}")

        # Add "Who this course is for" section
        try:
            who_for = course_detail['who_should_attend_data']['items']
            if who_for:
                description += '<h3><strong>Who this course is for:</strong></h3><ul>'
                for item in who_for:
                    description += f"<li>{item}</li>"
                description += "</ul>"
        except (KeyError, TypeError):
            logger.warning("No 'who this course is for' data available")

        return description

    def process_course_category(self, course_obj, category, course_detail):
        """Process course category, subcategory, and topics"""
        # Add category
        course_obj.category.add(category)

        # Process subcategory
        try:
            subcategory_title = course_detail['primary_subcategory']['title']
            subcategory, created = SubCategory.objects.get_or_create(
                title=subcategory_title,
                category=category,
                defaults={'slug': subcategory_title.lower().replace(' ', '-')}
            )
            course_obj.subcategory.add(subcategory)
            logger.info(f"Added subcategory: {subcategory_title}")
        except (KeyError, TypeError) as e:
            logger.warning(f"No subcategory data available: {str(e)}")

        # Process topics/labels
        try:
            labels = course_detail.get('course_has_labels', [])
            for label_data in labels:
                try:
                    topic_title = label_data['label']['title']
                    topic, created = Topic.objects.get_or_create(
                        title=topic_title,
                        defaults={'slug': topic_title.lower().replace(' ', '-')}
                    )
                    course_obj.topic.add(topic)
                except (KeyError, TypeError) as e:
                    logger.warning(f"Error processing topic: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing course labels: {str(e)}")

    def send_completion_email(self, subject, message, recipient_list=None):
        """Send completion email notification"""
        if recipient_list is None:
            recipient1 = os.getenv('EMAIL_HOST_USER')
            recipient2 = os.getenv('MANAGER_EMAIL')
            recipient_list = [recipient1, recipient2]

        try:
            from_email = settings.EMAIL_HOST_USER
            html_message = f'<h1>{subject}</h1><p>{message}</p>'
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
                html_message=html_message
            )
            logger.info("Completion email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send completion email: {str(e)}")

    def process_single_course(self, course_detail, target_category='Development'):
        """
        Process a single course from Udemy API data.

        Args:
            course_detail (dict): Course detail data from Udemy API
            target_category (str): Target category for the course

        Returns:
            tuple: (course_obj, created, updated) where created/updated are booleans
        """
        if not course_detail:
            return None, False, False

        course_title = course_detail.get('title', '').strip()
        if not course_title:
            return None, False, False

        provider = self.get_provider()
        user = self.get_user()
        category = self.get_or_create_category(target_category)

        # Check if course already exists
        existing_course = Course.objects.filter(
            title=course_title,
            provider=provider
        ).first()

        if existing_course:
            # Update existing course
            self.update_course_details(existing_course, course_detail)
            self.process_course_category(existing_course, category, course_detail)
            logger.info(f"Updated existing course: {course_title}")
            return existing_course, False, True
        else:
            # Create new course
            try:
                # Extract course information
                image_url = course_detail.get('image_480x270', '')
                author = course_detail.get('visible_instructors', [{}])[0].get('title', '')
                duration = course_detail.get('content_info', '')
                level = course_detail.get('instructional_level', '')
                course_url = f"https://www.udemy.com{course_detail.get('url', '')}"

                # Create course object
                course_obj = Course(
                    user=user,
                    provider=provider,
                    image_url=image_url,
                    title=course_title,
                    description=self.create_course_description(course_detail),
                    author=author,
                    duration=duration,
                    level=level,
                    course_url=course_url,
                )

                # Set pricing
                if course_detail.get('is_paid', False):
                    course_obj.price = 13.0
                else:
                    course_obj.is_free = True

                course_obj.has_certificate = True

                # Save course
                course_obj.save()

                # Process categories and topics
                self.process_course_category(course_obj, category, course_detail)

                # Update additional details
                self.update_course_details(course_obj, course_detail)

                logger.info(f"Created new course: {course_title}")
                return course_obj, True, False

            except Exception as e:
                logger.error(f"Error creating course {course_title}: {str(e)}")
                raise
