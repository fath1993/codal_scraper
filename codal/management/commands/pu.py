from django.core.management.base import BaseCommand

from codal.models import CompanyProfile
from codal.tasks import company_profile_updater


class Command(BaseCommand):
    def handle(self, *args, **options):
        company_profiles = CompanyProfile.objects.filter()
        for company_profile in company_profiles:
            company_profile_updater(company_profile)


