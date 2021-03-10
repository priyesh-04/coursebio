"""
Udacity Course Data Loader
Loads course data from Udacity JSON file since they don't offer a public API.
"""

import os
import json
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


class UdacityDataLoader:
    """
    Loads Udacity course data from JSON file.
    Since Udacity doesn't provide a public API, we use static JSON data.
    """

    def __init__(self, json_file_path=None):
        """
        Initialize Udacity data loader.

        Args:
            json_file_path (str): Path to the Udacity courses JSON file
        """
        if json_file_path:
            self.json_file_path = json_file_path
        else:
            # Default path relative to the courses directory
            self.json_file_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'other_course_platforms',
                'udacity_response.json'
            )

        self.courses_data = None
        self._load_data()

    def _load_data(self):
        """
        Load course data from JSON file.
        """
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Extract courses from the response
            if 'courses' in data:
                self.courses_data = data['courses']
                logger.info(f"Loaded {len(self.courses_data)} Udacity courses from JSON file")
            else:
                logger.error("No 'courses' key found in Udacity JSON data")
                self.courses_data = []

        except FileNotFoundError:
            logger.error(f"Udacity JSON file not found: {self.json_file_path}")
            self.courses_data = []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Udacity JSON file: {e}")
            self.courses_data = []
        except Exception as e:
            logger.error(f"Unexpected error loading Udacity data: {e}")
            self.courses_data = []

    def get_all_courses(self):
        """
        Get all courses from the loaded data.

        Returns:
            list: List of course dictionaries
        """
        return self.courses_data or []

    def get_course_by_key(self, course_key):
        """
        Get a specific course by its key.

        Args:
            course_key (str): Udacity course key

        Returns:
            dict: Course data or None if not found
        """
        for course in self.courses_data or []:
            if course.get('key') == course_key:
                return course
        return None

    def get_available_courses(self):
        """
        Get only courses that are available for enrollment.

        Returns:
            list: List of available courses
        """
        available_courses = []
        for course in self.courses_data or []:
            if course.get('available', False) and course.get('open_for_enrollment', False):
                available_courses.append(course)
        return available_courses

    def get_courses_by_level(self, level):
        """
        Get courses filtered by difficulty level.

        Args:
            level (str): Difficulty level (beginner, intermediate, advanced)

        Returns:
            list: List of courses matching the level
        """
        filtered_courses = []
        for course in self.courses_data or []:
            if course.get('level', '').lower() == level.lower():
                filtered_courses.append(course)
        return filtered_courses

    def get_courses_by_tags(self, tags):
        """
        Get courses that match any of the specified tags.

        Args:
            tags (list): List of tags to search for

        Returns:
            list: List of courses matching the tags
        """
        if not tags:
            return self.courses_data or []

        filtered_courses = []
        tag_set = set(tag.lower() for tag in tags)

        for course in self.courses_data or []:
            course_tags = course.get('tags', [])
            if course_tags:
                course_tag_set = set(tag.lower() for tag in course_tags)
                if tag_set.intersection(course_tag_set):
                    filtered_courses.append(course)

        return filtered_courses

    def get_course_url(self, course_key, course_slug=None):
        """
        Generate Udacity course URL.

        Args:
            course_key (str): Udacity course key
            course_slug (str): Course slug (optional)

        Returns:
            str: Full course URL
        """
        if course_slug:
            return f"https://www.udacity.com/course/{course_slug}"
        else:
            return f"https://www.udacity.com/course/{course_key}"

    def parse_duration(self, course_data):
        """
        Parse course duration from Udacity data.

        Args:
            course_data (dict): Course data from JSON

        Returns:
            str: Formatted duration string
        """
        duration = course_data.get('expected_duration', 0)
        duration_unit = course_data.get('expected_duration_unit', '')

        if duration and duration_unit:
            if duration == 1:
                return f"{duration} {duration_unit.rstrip('s')}"
            else:
                return f"{duration} {duration_unit}"
        elif duration:
            return f"{duration} months"  # Default assumption
        else:
            return None

    def parse_launch_date(self, date_string):
        """
        Parse launch date string into datetime object.

        Args:
            date_string (str): Date string in MM/DD/YYYY format

        Returns:
            datetime: Parsed datetime object or None
        """
        if not date_string:
            return None

        try:
            # Udacity uses MM/DD/YYYY format
            return datetime.strptime(date_string, '%m/%d/%Y')
        except ValueError:
            logger.warning(f"Could not parse date: {date_string}")
            return None

    def get_course_image_url(self, course_data):
        """
        Extract the best available image URL from course data.

        Args:
            course_data (dict): Course data from JSON

        Returns:
            str: Image URL or None
        """
        # Try different image fields in order of preference
        image_fields = ['image', 'card_image', 'banner_image']

        for field in image_fields:
            image_url = course_data.get(field)
            if image_url:
                return image_url

        return None

    def get_course_summary(self, course_data):
        """
        Get the best available course summary/description.

        Args:
            course_data (dict): Course data from JSON

        Returns:
            str: Course summary or None
        """
        # Try different description fields in order of preference
        summary_fields = ['summary', 'short_summary', 'expected_learning', 'subtitle']

        for field in summary_fields:
            summary = course_data.get(field)
            if summary:
                return summary

        return None

    def is_free_course(self, course_data):
        """
        Check if a course is free based on metadata.

        Args:
            course_data (dict): Course data from JSON

        Returns:
            bool: True if course is free
        """
        metadata = course_data.get('metadata', {})
        return metadata.get('is_free_course', False)

    def get_instructor_info(self, course_data):
        """
        Extract instructor information from course data.

        Args:
            course_data (dict): Course data from JSON

        Returns:
            list: List of instructor names
        """
        instructors = course_data.get('instructors', [])
        instructor_names = []

        for instructor in instructors:
            if isinstance(instructor, dict):
                # Handle instructor objects
                name = instructor.get('name', '').strip()
                if name:
                    instructor_names.append(name)
            elif isinstance(instructor, str):
                # Handle instructor names as strings
                instructor_names.append(instructor.strip())

        return instructor_names

    def reload_data(self):
        """
        Reload data from the JSON file.
        Useful if the file has been updated.
        """
        logger.info("Reloading Udacity course data")
        self._load_data()
