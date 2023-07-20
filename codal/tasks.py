import jdatetime
import time

from custom_logs.models import custom_log
from proxies.models import get_proxy, check_proxy_availability
from codal.cbot import get_codal_data, codal_first_page, get_time_sleep, check_if_last_page, codal_monthly_report_page, \
    codal_seasonal_report_page, monthly_report_calculator, seasonal_report_calculator, \
    seasonal_report_operating_ratio_calculator, get_monthly_report_number, get_seasonal_report_number
from codal.models import Company, CompanyLink, MonthlyReport, SeasonalReport, CompanyProfile


def run_thread():
    custom_log('thread starts')
    custom_log('now we are waiting for 90 seconds')
    time.sleep(90)
    custom_log('thread has been finished')
    return True


def codal_scraper():
    while True:
        # from first page
        custom_log("the robot has started task 1", 'p')
        while True:
            try:
                custom_log("check and update data with first page", 'p')
                get_codal_data(codal_first_page())
                custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                time.sleep(get_time_sleep())
                break
            except Exception as e:
                custom_log("problem has happened during the event : " + str(e), 'p')
                while True:
                    custom_log("checking proxy...", 'p')
                    if check_proxy_availability(get_proxy()):
                        break
                    else:
                        custom_log("proxies are not connectable. pls upgrade theme", 'p')
                        custom_log("we check proxy list again after 5 minute", 'p')
                        time.sleep(300)

        # from custom link
        companies = CompanyLink.objects.all()
        while companies.count() != 0:
            company = companies.latest('id')
            company_badge = company.badge
            company_link = company.link
            custom_log("cbot - نماد کمپانی : \n" + str(company_badge), 'p')
            custom_log("cbot - لینک کمپانی : \n" + str(company_link), 'p')
            n = 1
            while True:
                try:
                    while not check_if_last_page(codal_monthly_report_page(company_link, n)):
                        custom_log(
                            str(get_time_sleep()) + "second delay after checking " + company_badge + " monthly last page",
                            'p')
                        time.sleep(get_time_sleep())
                        while True:
                            try:
                                custom_log("check and update data with first page", 'p')
                                get_codal_data(codal_first_page())
                                custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                                time.sleep(get_time_sleep())
                                break
                            except Company.DoesNotExist as e:
                                custom_log("company problem : " + str(e), 'p')
                                break
                            except Exception as e:
                                custom_log("problem has happened during the event : " + str(e), 'p')
                                while True:
                                    custom_log("checking proxy...", 'p')
                                    if check_proxy_availability(get_proxy()):
                                        break
                                    else:
                                        custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                        custom_log("we check proxy list again after 5 minute", 'p')
                                        time.sleep(300)
                        while True:
                            try:
                                custom_log("check and update " + company_badge + " monthly report", 'p')
                                get_codal_data(codal_monthly_report_page(company_link, n))
                                custom_log(str(get_time_sleep()) + "second delay after getting monthly report", 'p')
                                time.sleep(get_time_sleep())
                                break
                            except Company.DoesNotExist as e:
                                custom_log("company problem : " + str(e), 'p')
                                break
                            except Exception as e:
                                custom_log("problem has happened during the event : " + str(e), 'p')
                                while True:
                                    custom_log("checking proxy...", 'p')
                                    if check_proxy_availability(get_proxy()):
                                        break
                                    else:
                                        custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                        custom_log("we check proxy list again after 5 minute", 'p')
                                        time.sleep(300)
                        n += 1
                    break
                except Company.DoesNotExist as e:
                    custom_log("company problem : " + str(e), 'p')
                    n += 1
                except Exception as e:
                    custom_log("problem has happened during the event : " + str(e), 'p')
                    while True:
                        custom_log("checking proxy...", 'p')
                        if check_proxy_availability(get_proxy()):
                            break
                        else:
                            custom_log("proxies are not connectable. pls upgrade theme", 'p')
                            custom_log("we check proxy list again after 5 minute", 'p')
                            time.sleep(300)
            n = 1
            while True:
                try:
                    while not check_if_last_page(codal_seasonal_report_page(company_link, n)):
                        custom_log(
                            str(get_time_sleep()) + "second delay after checking " + company_badge + " seasonal last page",
                            'p')
                        time.sleep(get_time_sleep())
                        while True:
                            try:
                                custom_log("check and update data with first page", 'p')
                                get_codal_data(codal_first_page())
                                custom_log(str(get_time_sleep()) + "second delay after updating data with first page",
                                           'p')
                                time.sleep(get_time_sleep())
                                break
                            except Company.DoesNotExist as e:
                                custom_log("company problem : " + str(e), 'p')
                                break
                            except Exception as e:
                                custom_log("problem has happened during the event : " + str(e), 'p')
                                while True:
                                    custom_log("checking proxy...", 'p')
                                    if check_proxy_availability(get_proxy()):
                                        break
                                    else:
                                        custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                        custom_log("we check proxy list again after 5 minute", 'p')
                                        time.sleep(300)
                        while True:
                            try:
                                custom_log("check and update " + company_badge + " seasonal report", 'p')
                                get_codal_data(codal_seasonal_report_page(company_link, n))
                                custom_log(str(get_time_sleep()) + "second delay after getting seasonal report", 'p')
                                time.sleep(get_time_sleep())
                                break
                            except Company.DoesNotExist as e:
                                custom_log("company problem : " + str(e), 'p')
                                break
                            except Exception as e:
                                custom_log("problem has happened during the event : " + str(e), 'p')
                                while True:
                                    custom_log("checking proxy...", 'p')
                                    if check_proxy_availability(get_proxy()):
                                        break
                                    else:
                                        custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                        custom_log("we check proxy list again after 5 minute", 'p')
                                        time.sleep(300)
                        n += 1
                    break
                except Company.DoesNotExist as e:
                    custom_log("company problem : " + str(e), 'p')
                    n += 1
                except Exception as e:
                    custom_log("problem has happened during the event : " + str(e), 'p')
                    while True:
                        custom_log("checking proxy...", 'p')
                        if check_proxy_availability(get_proxy()):
                            break
                        else:
                            custom_log("proxies are not connectable. pls upgrade theme", 'p')
                            custom_log("we check proxy list again after 5 minute", 'p')
                            time.sleep(300)

            mr = MonthlyReport.objects.filter(is_finished=False)
            for item in mr:
                while True:
                    try:
                        custom_log("getting " + str(item) + " monthly report data", 'p')
                        get_monthly_report_number(item)
                        cc = Company.objects.get(monthly_report=item)
                        cc.save()
                        custom_log("getting " + str(item) + " monthly report has finished. we are waiting for " + str(get_time_sleep()) + " seconds",
                               'p')
                        time.sleep(get_time_sleep())
                        break
                    except Company.DoesNotExist as e:
                        custom_log("company problem : " + str(e), 'p')
                        break
                    except Exception as e:
                        custom_log("problem has happened during the event : " + str(e), 'p')
                        while True:
                            custom_log("checking proxy...", 'p')
                            if check_proxy_availability(get_proxy()):
                                break
                            else:
                                custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                custom_log("we check proxy list again after 5 minute", 'p')
                                time.sleep(300)
                while True:
                    try:
                        custom_log("check and update data with first page", 'p')
                        get_codal_data(codal_first_page())
                        custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                        time.sleep(get_time_sleep())
                        break
                    except Company.DoesNotExist as e:
                        custom_log("company problem : " + str(e), 'p')
                        break
                    except Exception as e:
                        custom_log("problem has happened during the event : " + str(e), 'p')
                        while True:
                            custom_log("checking proxy...", 'p')
                            if check_proxy_availability(get_proxy()):
                                break
                            else:
                                custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                custom_log("we check proxy list again after 5 minute", 'p')
                                time.sleep(300)
            sr = SeasonalReport.objects.filter(is_finished=False)
            for item in sr:
                while True:
                    try:
                        custom_log("getting " + str(item) + " seasonal report data", 'p')
                        get_seasonal_report_number(item)
                        cc = Company.objects.get(seasonal_report=item)
                        cc.save()
                        custom_log("getting " + str(item) + " seasonal report has finished. we are waiting for " + str(get_time_sleep()) + " seconds",
                               'p')
                        time.sleep(get_time_sleep())
                        break
                    except Company.DoesNotExist as e:
                        custom_log("company problem : " + str(e), 'p')
                        break
                    except Exception as e:
                        custom_log("problem has happened during the event : " + str(e), 'p')
                        while True:
                            custom_log("checking proxy...", 'p')
                            if check_proxy_availability(get_proxy()):
                                break
                            else:
                                custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                custom_log("we check proxy list again after 5 minute", 'p')
                                time.sleep(300)
                while True:
                    try:
                        custom_log("check and update data with first page", 'p')
                        get_codal_data(codal_first_page())
                        custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                        time.sleep(get_time_sleep())
                        break
                    except Company.DoesNotExist as e:
                        custom_log("company problem : " + str(e), 'p')
                        break
                    except Exception as e:
                        custom_log("problem has happened during the event : " + str(e), 'p')
                        while True:
                            custom_log("checking proxy...", 'p')
                            if check_proxy_availability(get_proxy()):
                                break
                            else:
                                custom_log("proxies are not connectable. pls upgrade theme", 'p')
                                custom_log("we check proxy list again after 5 minute", 'p')
                                time.sleep(300)
            company.delete()
            custom_log("---------------------------------- next -------------------------------", 'p')
        custom_log("the robot has finished task 1", 'p')

        # from first page
        custom_log("the robot has started task 2", 'p')
        while True:
            try:
                custom_log("check and update data with first page", 'p')
                get_codal_data(codal_first_page())
                custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                time.sleep(get_time_sleep())
                break
            except Company.DoesNotExist as e:
                custom_log("company problem : " + str(e), 'p')
                break
            except Exception as e:
                custom_log("problem has happened during the event : " + str(e), 'p')
                while True:
                    custom_log("checking proxy...", 'p')
                    if check_proxy_availability(get_proxy()):
                        break
                    else:
                        custom_log("proxies are not connectable. pls upgrade theme", 'p')
                        custom_log("we check proxy list again after 5 minute", 'p')
                        time.sleep(300)
        mr = MonthlyReport.objects.filter(is_finished=False)
        for item in mr:
            while True:
                try:
                    custom_log("getting " + str(item) + " monthly report data", 'p')
                    get_monthly_report_number(item)
                    cc = Company.objects.get(monthly_report=item)
                    cc.save()
                    custom_log("getting " + str(item) + " monthly report has finished. we are waiting for " + str(get_time_sleep()) + " seconds", 'p')
                    time.sleep(get_time_sleep())
                    break
                except Company.DoesNotExist as e:
                    custom_log("company problem : " + str(e), 'p')
                    break
                except Exception as e:
                    custom_log("problem has happened during the event : " + str(e), 'p')
                    while True:
                        custom_log("checking proxy...", 'p')
                        if check_proxy_availability(get_proxy()):
                            break
                        else:
                            custom_log("proxies are not connectable. pls upgrade theme", 'p')
                            custom_log("we check proxy list again after 5 minute", 'p')
                            time.sleep(300)
            while True:
                try:
                    custom_log("check and update data with first page", 'p')
                    get_codal_data(codal_first_page())
                    custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                    time.sleep(get_time_sleep())
                    break
                except Company.DoesNotExist as e:
                    custom_log("company problem : " + str(e), 'p')
                    break
                except Exception as e:
                    custom_log("problem has happened during the event : " + str(e), 'p')
                    while True:
                        custom_log("checking proxy...", 'p')
                        if check_proxy_availability(get_proxy()):
                            break
                        else:
                            custom_log("proxies are not connectable. pls upgrade theme", 'p')
                            custom_log("we check proxy list again after 5 minute", 'p')
                            time.sleep(300)
        sr = SeasonalReport.objects.filter(is_finished=False)
        for item in sr:
            while True:
                try:
                    custom_log("getting " + str(item) + " seasonal report data", 'p')
                    get_seasonal_report_number(item)
                    cc = Company.objects.get(seasonal_report=item)
                    cc.save()
                    custom_log("getting " + str(item) + " seasonal report has finished. we are waiting for " + str(get_time_sleep()) + " seconds", 'p')
                    time.sleep(get_time_sleep())
                    break
                except Company.DoesNotExist as e:
                    custom_log("company problem : " + str(e), 'p')
                    break
                except Exception as e:
                    custom_log("problem has happened during the event : " + str(e), 'p')
                    while True:
                        custom_log("checking proxy...", 'p')
                        if check_proxy_availability(get_proxy()):
                            break
                        else:
                            custom_log("proxies are not connectable. pls upgrade theme", 'p')
                            custom_log("we check proxy list again after 5 minute", 'p')
                            time.sleep(300)
            while True:
                try:
                    custom_log("check and update data with first page", 'p')
                    get_codal_data(codal_first_page())
                    custom_log(str(get_time_sleep()) + "second delay after updating data with first page", 'p')
                    time.sleep(get_time_sleep())
                    break
                except Company.DoesNotExist as e:
                    custom_log("company problem : " + str(e), 'p')
                    break
                except Exception as e:
                    custom_log("problem has happened during the event : " + str(e), 'p')
                    while True:
                        custom_log("checking proxy...", 'p')
                        if check_proxy_availability(get_proxy()):
                            break
                        else:
                            custom_log("proxies are not connectable. pls upgrade theme", 'p')
                            custom_log("we check proxy list again after 5 minute", 'p')
                            time.sleep(300)
        custom_log("the robot has finished task 2", 'p')


def company_profile_updater():
    while True:
        company_profiles = CompanyProfile.objects.filter()
        for company_profile in company_profiles:
            company_profile_updater(company_profile)
            try:
                custom_log("company_profile_updater> start", 'd')
                monthly_report_calculator(company_profile)
                seasonal_report_calculator(company_profile)
                seasonal_report_operating_ratio_calculator(company_profile)
            except Exception as e:
                custom_log("company_profile_updater>try/except err: " + str(e), 'd')
            custom_log("company_profile_updater> finish", 'd')
            custom_log("company_profile_updater> waiting for 1 hour", 'd')
        time.sleep(3600)



