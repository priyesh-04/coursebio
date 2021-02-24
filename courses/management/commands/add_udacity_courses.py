from django.core.management.base import BaseCommand, CommandError
from courses.udacity_tasks import udacity

class Command(BaseCommand):

    def handle(self, *args, **options):
        udacity()
        return 'success'