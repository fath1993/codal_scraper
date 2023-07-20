from django.core.management.base import BaseCommand
from custom_logs.models import CustomLog
from codal.models import Company, MonthlyReport, SeasonalReport, CompanyLink
from proxies.models import Proxy


def clear_data():
    Company.objects.all().delete()
    MonthlyReport.objects.all().delete()
    SeasonalReport.objects.all().delete()
    #CompanyLink.objects.all().delete()
    CustomLog.objects.all().delete()
    Proxy.objects.all().delete()


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_data()
