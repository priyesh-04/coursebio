"""
edX API Client
Handles authentication and API calls to edX platform.
"""

import os
import requests
import logging
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class EdxAPI:
    """
    edX API client for course data retrieval.
    """

    def __init__(self, client_id=None, client_secret=None, base_url=None):
        """
        Initialize edX API client.

        Args:
            client_id (str): edX API client ID
            client_secret (str): edX API client secret
            base_url (str): Base URL for edX API
        """
        self.client_id = client_id or os.getenv('EDX_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('EDX_CLIENT_SECRET')
        self.base_url = base_url or os.getenv('EDX_API_URL', 'https://courses.edx.org/api')
        self.session = requests.Session()
        self.access_token = None
        self.token_expires = None

    def _get_access_token(self):
        """
        Get access token for edX API authentication.
        Note: edX API might not require OAuth2 authentication for public course data.
        This method is prepared for future authentication requirements.
        """
        if self.client_id and self.client_secret:
            # Prepare for OAuth2 authentication if needed
            auth_url = urljoin(self.base_url, '/oauth2/access_token/')
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'read'
            }

            try:
                response = self.session.post(auth_url, data=data)
                response.raise_for_status()
                token_data = response.json()

                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires = datetime.now().timestamp() + expires_in

                logger.info("Successfully obtained edX API access token")
                return True

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get edX API access token: {e}")
                return False
        else:
            logger.info("No edX API credentials provided - using public API access")
            return True

    def _make_request(self, endpoint, params=None, method='GET'):
        """
        Make authenticated request to edX API.

        Args:
            endpoint (str): API endpoint
            params (dict): Query parameters
            method (str): HTTP method

        Returns:
            dict: API response data
        """
        url = urljoin(self.base_url, endpoint)

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'CourseBio-edX-Integration/1.0'
        }

        # Add authentication header if token is available
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'

        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            else:
                response = self.session.request(method, url, headers=headers, params=params)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"edX API request failed: {e}")
            raise

    def courses(self, page=1, page_size=100, search=None, org=None):
        """
        Get courses from edX API.

        Args:
            page (int): Page number
            page_size (int): Number of courses per page
            search (str): Search query
            org (str): Filter by organization

        Returns:
            dict: Courses data with pagination
        """
        endpoint = '/courses/v1/courses/'

        params = {
            'page': page,
            'page_size': page_size,
        }

        if search:
            params['search'] = search

        if org:
            params['org'] = org

        logger.info(f"Fetching edX courses - page: {page}, page_size: {page_size}")
        return self._make_request(endpoint, params)

    def course_detail(self, course_id):
        """
        Get detailed information for a specific course.

        Args:
            course_id (str): edX course ID

        Returns:
            dict: Course detail data
        """
        endpoint = f'/courses/v1/courses/{course_id}/'

        logger.info(f"Fetching edX course details for: {course_id}")
        return self._make_request(endpoint)

    def course_blocks(self, course_id):
        """
        Get course blocks/structure for a specific course.

        Args:
            course_id (str): edX course ID

        Returns:
            dict: Course blocks data
        """
        endpoint = '/courses/v2/blocks/'
        params = {'course_id': course_id}

        logger.info(f"Fetching edX course blocks for: {course_id}")
        return self._make_request(endpoint, params)

    def get_course_url(self, course_id):
        """
        Generate course URL from course ID.

        Args:
            course_id (str): edX course ID

        Returns:
            str: Full course URL
        """
        # Convert course ID format to URL format
        # Example: "AdelaideX/HumBio101x/1T2015" -> "course-v1:AdelaideX+HumBio101x+1T2015"
        course_url_id = course_id.replace('/', '+')
        return f"https://courses.edx.org/courses/course-v1:{course_url_id}/"

    def get_course_image_url(self, course_data):
        """
        Extract the best available image URL from course data.

        Args:
            course_data (dict): Course data from API

        Returns:
            str: Image URL or None
        """
        media = course_data.get('media', {})

        # Try different image sources in order of preference
        image_sources = [
            media.get('image', {}).get('large'),
            media.get('image', {}).get('raw'),
            media.get('course_image', {}).get('uri_absolute'),
            media.get('banner_image', {}).get('uri_absolute'),
        ]

        for image_url in image_sources:
            if image_url:
                return image_url

        return None

    def get_course_video_url(self, course_data):
        """
        Extract video URL from course data.

        Args:
            course_data (dict): Course data from API

        Returns:
            str: Video URL or None
        """
        media = course_data.get('media', {})
        course_video = media.get('course_video', {})

        if course_video and course_video.get('uri'):
            return course_video['uri']

        return None

    def parse_effort(self, effort_string):
        """
        Parse effort string into a standardized duration format.

        Args:
            effort_string (str): Effort description (e.g., "12 hours/week", "03:00")

        Returns:
            str: Standardized duration string
        """
        if not effort_string:
            return None

        effort = effort_string.strip()

        # Handle different effort formats
        if 'hour' in effort.lower():
            if 'week' in effort.lower():
                return effort  # Already in good format like "12 hours/week"
            else:
                return f"{effort} hours"
        elif ':' in effort:
            # Handle time format like "03:00"
            try:
                hours, minutes = effort.split(':')
                hours = int(hours)
                minutes = int(minutes)
                if hours > 0:
                    return f"{hours} hours {minutes} minutes" if minutes > 0 else f"{hours} hours"
                else:
                    return f"{minutes} minutes"
            except ValueError:
                return effort
        else:
            return effort
