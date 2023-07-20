from django.core.management.base import BaseCommand
from codal.tasks import codal_scraper


class Command(BaseCommand):
    def handle(self, *args, **options):
        codal_scraper()


