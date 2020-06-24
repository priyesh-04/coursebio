
# This command is to remove extra slash 
# from udemy courses course_url field.

from django.core.management.base import BaseCommand, CommandError
from courses.models import Course

class Command(BaseCommand):

    def handle(self, *args, **options):
        _courses = Course.objects.all()
        for course in _courses:
        	url = course.course_url
        	if "https://www.udemy.com//" in url:
        		course.course_url = url[:21] + url[(21+1):]
        		course.save()
        		print(course.title,"url updated")
        return 'success'