from django.core.management.base import BaseCommand
from codal.tasks import codal_scraper, run_thread


class Command(BaseCommand):
    def handle(self, *args, **options):
        run_thread()


