from django.core.management.base import BaseCommand, CommandError
from courses.tasks import udemy

class Command(BaseCommand):

    def handle(self, *args, **options):
        udemy()
        return 'success'