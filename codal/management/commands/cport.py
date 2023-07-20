from django.core.management.base import BaseCommand

from codal.models import CompanyLink


def companies_link_import(file_txt_address_link, file_txt_address_badge):
    badge_list = []
    with open(file=file_txt_address_badge, mode="r", encoding='utf-8') as f:
        text = f.readlines()
        for line in text:
            badge_list.append(line)
    with open(file=file_txt_address_link, mode="r") as f:
        text = f.readlines()
        i = 0
        for line in text:
            try:
                company_link = CompanyLink.objects.get(badge=badge_list[i], link=line)
                print("company had already exist : " + str(badge_list[i]) + " - " + str(line))
            except:
                new_company_link = CompanyLink(
                    badge=badge_list[i],
                    link=line,
                )
                new_company_link.save()
                print("new company: " + str(badge_list[i]) + " - " + str(line))
            i += 1
            if i == 3:
                break


class Command(BaseCommand):
    def handle(self, *args, **options):
        companies_link_import("codal_companies_08_14_2022.txt", "codal_companies_08_14_2022_badge.txt")

