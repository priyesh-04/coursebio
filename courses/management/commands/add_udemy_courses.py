from django.core.management.base import BaseCommand, CommandError
from courses.udemy_tasks2 import udemy

class Command(BaseCommand):

    def handle(self, *args, **options):
        udemy()
        return 'success'