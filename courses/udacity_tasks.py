from __future__ import absolute_import, unicode_literals
import random

import operator
import requests
from requests.auth import HTTPBasicAuth

from courses.models import Category, SubCategory, Provider, Course, Topic
from django.conf import settings
from django.core.mail import send_mail

def udacity():
	# user = MyUser.objects.get(email='priyesh.shukla070@gmail.com')
	provider = Provider.objects.get(title='Udemy')
	present_courses_count = Course.objects.filter(provider__title='Udacity').count()

	# api-endpoint
	URL = 'https://catalog-api.udacity.com/v1/courses'
	r = requests.get(url=URL)
	data = r.json()

	# for i in range(len(data['results'])):
		

	