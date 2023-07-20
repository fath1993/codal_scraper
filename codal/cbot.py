import jdatetime
import time
from custom_logs.models import custom_log
from proxies.models import get_proxy, check_proxy_availability
from codal.models import Company, MonthlyReport, SeasonalReport, ConfigSetting
from codal.utils import date_extractor, year_extractor, word_simplifier, codal_title_cleanup, date_range_generator


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# 3.142.7

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver import FirefoxOptions, FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager


# ------------ Start Scraper functions -------------------
def get_time_sleep():
    settings = ConfigSetting.objects.all().latest('id')
    if not settings:
        time_sleep = 30
    else:
        time_sleep = settings.sleep_time
        custom_log("sleep time: " + str(time_sleep), "d")
    return int(time_sleep)


def get_codal_data(url):
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    settings = ConfigSetting.objects.filter().latest('id')
    firefox_profile = webdriver.FirefoxProfile()
    if settings.is_proxy_on:
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.http", get_proxy()[0])
        firefox_profile.set_preference("network.proxy.http_port", get_proxy()[1])
        firefox_profile.update_preferences()
        options.profile = firefox_profile
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    webdriver_problem_number_of_reloading = 0
    while True:
        try:
            number_of_reloading_page = 0
            while True:
                custom_log("get_codal_data: starting page load", "d")
                driver.get(url)
                custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()), 'd')
                time.sleep(get_time_sleep())
                custom_log("get_codal_data: spinner start", "d")
                try:
                    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner")))
                    try:
                        retry_button = driver.find_element(By.XPATH,
                                                           "/html/body/form/div[3]/div[1]/div[1]/div[2]/div[2]/div/div/input")
                        custom_log("get_codal_data: loading of page has been failed. error: صفحه لود نشد", "d")
                        custom_log("waiting for: " + str(get_time_sleep()) + " seconds", "d")
                        time.sleep(get_time_sleep())
                    except:
                        break
                except Exception as e:
                    custom_log("get_codal_data: spinner problem, 30 second passed and spinner still spinning", "d")
                number_of_reloading_page += 1
                if number_of_reloading_page == 3:
                    driver.quit()
                    return custom_log(
                        "get_codal_data: after reloading had been tried 3 times, this page has not been received and passed",
                        "d")
            try:
                tbody = driver.find_element(By.XPATH,
                                            "/html/body/form/div[3]/div[1]/div[1]/div[2]/div[2]/table/tbody")
                tr = tbody.find_elements(By.TAG_NAME, "tr")
                for i in tr:
                    custom_log("______________________ start ____________________________", "d")
                    td = i.find_elements(By.CLASS_NAME, "table__content")

                    # td[0]>>>>>badge#
                    badge = td[0].text.strip()
                    badge_link = td[0].find_element(By.TAG_NAME, "a").get_attribute('href')

                    # td[1]>>>>>name#
                    name = td[1].text.strip()

                    # td[3]>>>>>description#
                    description = td[3].text.strip()
                    description_detail = codal_title_cleanup(description)
                    print('description_detail: ' + str(description_detail))
                    report_status = []
                    for status in description_detail[1]:
                        if description_detail[1][status]:
                            report_status.append(status)
                    report_status = ' - '.join(report_status)
                    print(report_status)
                    comparative_title = word_simplifier(description_detail[0], 'without_space')
                    extracted_date = date_extractor(description)
                    generated_title = word_simplifier(description_detail[0], 'with_space') + str(extracted_date)
                    description_link = td[3].find_element(By.TAG_NAME, "a").get_attribute('href')
                    custom_log("badge: " + badge, "d")
                    custom_log("badge link: " + badge_link, "d")
                    custom_log("name: " + name, "d")
                    custom_log("description: " + description, "d")
                    custom_log("description link: " + description_link, "d")

                    # td[5]>>>>>date of publish
                    report_has_sent_at = str(td[5].text.strip()).replace('/', ' ').replace(':', ' ').split()
                    report_has_sent_at = jdatetime.datetime(year=int(report_has_sent_at[0]),
                                                            month=int(report_has_sent_at[1]),
                                                            day=int(report_has_sent_at[2]),
                                                            hour=int(report_has_sent_at[3]),
                                                            minute=int(report_has_sent_at[4]),
                                                            second=int(report_has_sent_at[5]))
                    try:
                        ye = year_extractor(description)
                        custom_log("the year is: " + ye, "d")
                        try:
                            if int(ye) >= 1400:
                                try:
                                    old_company = Company.objects.get(badge=badge)
                                    old_company.save()
                                    custom_log("this company exist" + " : " + badge, "d")
                                    if comparative_title.find("گزارشفعالیتماهانهدوره۱ماههمنتهیبه") != -1:
                                        try:
                                            old_report = MonthlyReport.objects.get(report_title=generated_title,
                                                                                   company=old_company)
                                            try:
                                                if old_report.report_has_sent_at < report_has_sent_at:
                                                    old_report.report_link = description_link
                                                    old_report.report_has_sent_at = report_has_sent_at
                                                    old_report.report_status = report_status
                                                    old_report.month_reported_date = extracted_date
                                                    old_report.save()
                                                    custom_log(
                                                        "this monthly report exist" + " : " + old_company.name + " - " + old_report.report_title + " and updated",
                                                        "d")
                                                else:
                                                    custom_log(
                                                        "ignore similar report" + old_company.name + " - " + old_report.report_title,
                                                        "d")
                                            except Exception as e:
                                                custom_log("try->except: old report data\n" + str(e), "d")
                                        except Exception as e:
                                            custom_log("try->except: old report\n" + str(e), "d")
                                            try:
                                                new_report = MonthlyReport(
                                                    company=old_company,
                                                    report_title=generated_title,
                                                    report_link=description_link,
                                                    month_reported_date=extracted_date,
                                                    report_has_sent_at=report_has_sent_at,
                                                    report_status=report_status,
                                                )
                                                new_report.save()
                                                custom_log(
                                                    "the new monthly report : " + badge + " - " + generated_title + " has been saved",
                                                    "d")
                                            except Exception as e:
                                                custom_log("try->except: new report\n" + str(e), "d")
                                    elif comparative_title.find("اطلاعاتوصورت‌هایمالیمیاندوره‌ای") != -1 \
                                            or comparative_title.find("صورت‌هایمالیسالمالیمنتهیبه") != -1 \
                                            or comparative_title.find(
                                        "صورت‌هایمالیتلفیقیسالمالیمنتهیبه") != -1:
                                        try:
                                            old_report = SeasonalReport.objects.get(report_title=generated_title,
                                                                                    company=old_company)
                                            try:
                                                if old_report.report_has_sent_at < report_has_sent_at:
                                                    old_report.report_link = description_link
                                                    old_report.report_has_sent_at = report_has_sent_at
                                                    old_report.report_status = report_status
                                                    old_report.season_reported_date = extracted_date
                                                    old_report.save()
                                                    custom_log(
                                                        "this seasonal report exist" + " : " + old_company.name + " - " + old_report.report_title + " and updated",
                                                        "d")
                                                else:
                                                    custom_log(
                                                        "ignore similar report" + old_company.name + " - " + old_report.report_title,
                                                        "d")
                                            except Exception as e:
                                                custom_log("try->except: old report data\n" + str(e), "d")
                                        except Exception as e:
                                            custom_log("try->except: old report\n" + str(e), "d")
                                            try:
                                                new_report = SeasonalReport(
                                                    company=old_company,
                                                    report_title=generated_title,
                                                    report_link=description_link,
                                                    season_reported_date=extracted_date,
                                                    report_has_sent_at=report_has_sent_at,
                                                    report_status=report_status,
                                                )
                                                new_report.save()
                                                custom_log(
                                                    "the new seasonal report : " + badge + " - " + generated_title + " has been saved",
                                                    "d")
                                            except Exception as e:
                                                custom_log("try->except: new report" + str(e), "d")
                                    else:
                                        custom_log("گزارش این بخش با فرمت های تعریف شده سازگار نیست", 'd')
                                except Exception as e:
                                    custom_log("try->except: old company\n" + str(e), "d")
                                    try:
                                        new_company = Company(
                                            badge=badge,
                                            link=badge_link,
                                            name=name,
                                        )
                                        new_company.save()
                                        custom_log("the new company : " + badge + " has saved", "d")
                                        if comparative_title.find("گزارشفعالیتماهانهدوره۱ماههمنتهیبه") != -1:
                                            try:
                                                old_report = MonthlyReport.objects.get(report_title=generated_title,
                                                                                       company=new_company)
                                                try:
                                                    if old_report.report_has_sent_at < report_has_sent_at:
                                                        old_report.report_link = description_link
                                                        old_report.report_has_sent_at = report_has_sent_at
                                                        old_report.report_status = report_status
                                                        old_report.month_reported_date = extracted_date
                                                        old_report.save()
                                                        custom_log(
                                                            "this monthly report exist" + " : " + new_company.name + " - " + old_report.report_title + " and updated",
                                                            "d")
                                                    else:
                                                        custom_log(
                                                            "ignore similar report" + new_company.name + " - " + old_report.report_title,
                                                            "d")
                                                except Exception as e:
                                                    custom_log("try->except: old report data" + str(e), "d")
                                            except Exception as e:
                                                custom_log("try->except: old report" + str(e), "d")
                                                try:
                                                    new_report = MonthlyReport(
                                                        company=new_company,
                                                        report_title=generated_title,
                                                        report_link=description_link,
                                                        month_reported_date=extracted_date,
                                                        report_has_sent_at=report_has_sent_at,
                                                        report_status=report_status,
                                                    )
                                                    new_report.save()
                                                    custom_log(
                                                        "the new monthly report : " + badge + " - " + generated_title + " has saved",
                                                        "d")
                                                except Exception as e:
                                                    custom_log("try->except: new report" + str(e), "d")
                                        elif comparative_title.find("اطلاعاتوصورت‌هایمالیمیاندوره‌ای") != -1 \
                                                or comparative_title.find("صورت‌هایمالیسالمالیمنتهیبه") != -1 \
                                                or comparative_title.find(
                                            "صورت‌هایمالیتلفیقیسالمالیمنتهیبه") != -1:
                                            try:
                                                old_report = SeasonalReport.objects.get(report_title=generated_title,
                                                                                        company=new_company)
                                                try:
                                                    if old_report.report_has_sent_at < report_has_sent_at:
                                                        old_report.report_link = description_link
                                                        old_report.report_has_sent_at = report_has_sent_at
                                                        old_report.report_status = report_status
                                                        old_report.season_reported_date = extracted_date
                                                        old_report.save()
                                                        custom_log(
                                                            "this seasonal report exist" + " : " + new_company.name + " - " + old_report.report_title + " and updated",
                                                            "d")
                                                    else:
                                                        custom_log(
                                                            "ignore similar report" + new_company.name + " - " + old_report.report_title,
                                                            "d")
                                                except Exception as e:
                                                    custom_log("try->except: old report data" + str(e), "d")
                                            except Exception as e:
                                                custom_log("try->except: old report" + str(e), "d")
                                                try:
                                                    new_report = SeasonalReport(
                                                        company=new_company,
                                                        report_title=generated_title,
                                                        report_link=description_link,
                                                        season_reported_date=extracted_date,
                                                        report_has_sent_at=report_has_sent_at,
                                                        report_status=report_status,
                                                    )
                                                    new_report.save()
                                                    custom_log(
                                                        "the new seasonal report : " + badge + " - " + generated_title + " has been saved",
                                                        "d")
                                                except Exception as e:
                                                    custom_log("try->except: new report " + str(e), "d")
                                        else:
                                            custom_log("گزارش این بخش با فرمت های تعریف شده سازگار نیست", 'd')
                                    except Exception as e:
                                        custom_log("try->except: new company cant create \n" + str(e), "d")
                            else:
                                custom_log("this report is older than 1400", "d")
                        except Exception as e:
                            custom_log("exception: " + str(e), 'd')
                    except Exception as e:
                        custom_log(
                            "report year extraction has been failed. title is: " + generated_title + ' err: ' + str(e),
                            "d")
                    custom_log("______________________ end ____________________________", "d")
            except Exception as e:
                custom_log("try->except: get_codal_data tbody " + str(e), "d")
            break
        except NoSuchElementException as noelement:
            custom_log('get_codal_data no such element exception: ' + str(noelement), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except WebDriverException as driver_exception:
            custom_log('get_codal_data webdriver exception: ' + str(driver_exception), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            raise e
        except Exception as e:
            custom_log('get_codal_data other exception: ' + str(e), "d")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', "d")
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            return custom_log(
                "get_codal_data: after reloading had been tried 3 times, this webdriver exceptions still exist", 'd')
    custom_log('get_codal_data:' + str(url) + ' | complete', "d")
    driver.quit()


def get_monthly_report_number(report_object):
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    settings = ConfigSetting.objects.filter().latest('id')
    firefox_profile = webdriver.FirefoxProfile()
    if settings.is_proxy_on:
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.http", get_proxy()[0])
        firefox_profile.set_preference("network.proxy.http_port", get_proxy()[1])
        firefox_profile.update_preferences()
        options.profile = firefox_profile
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    webdriver_problem_number_of_reloading = 0
    while True:
        try:
            number_of_reloading_page = 0
            while True:
                custom_log("get_monthly_report_number: starting page load", "d")
                url = report_object.report_link
                driver.get(url)
                custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()), 'd')
                time.sleep(get_time_sleep())
                try:
                    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner")))
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, "label")))
                    try:
                        retry_button = driver.find_element(By.XPATH,
                                                           "/html/body/form/div[3]/div[1]/div[1]/div[2]/div[2]/div/div/input")
                        custom_log("get_monthly_report_number: loading of page has been failed. error: صفحه لود نشد",
                                   "d")
                        custom_log("waiting for: " + "60" + "seconds", "d")
                        time.sleep(get_time_sleep())
                    except Exception as e:
                        custom_log("try->except get_monthly_report_number retry_button", 'd')
                        break
                except Exception as e:
                    custom_log(
                        "get_monthly_report_number: page timeout problem, 30 second passed and nothing happened - " + str(
                            e), 'd')
                number_of_reloading_page += 1
                if number_of_reloading_page == 3:
                    driver.quit()
                    return custom_log(
                        "get_monthly_report_number: after reloading had been tried 3 times, this page has not been received and passed",
                        'd')
            page_is_ok = False
            try:
                option_ = driver.find_elements(By.TAG_NAME, 'option')
                for op in option_:
                    op_text = word_simplifier(op.text.strip(), 'without_space')
                    if op_text == "گزارشفعالیتماهانه":
                        page_is_ok = True
                        custom_log("get_monthly_report_number | page_is_ok? : " + "TRUE", 'd')
            except:
                print("get_monthly_report_number | page_is_ok? : " + "FALSE")
            if page_is_ok:
                while True:
                    try:
                        table_title = driver.find_element(By.CLASS_NAME, "table-title")
                        app_table = driver.find_elements(By.CLASS_NAME, "rayanDynamicStatement")[0]
                        tbody = app_table.find_element(By.TAG_NAME, 'tbody')
                        tr = tbody.find_elements(By.TAG_NAME, "tr")
                        last_tr = tr[len(tr) - 1]
                        td = last_tr.find_elements(By.TAG_NAME, "td")
                        table_title_text = word_simplifier(table_title.text, 'without_space')

                        if table_title_text == "تولیدوفروش":
                            try:
                                custom_log("report url: " + url, 'd')
                                custom_log("category is: " + "تولید و فروش", 'd')
                                custom_log("reported_number is: " + td[16].text, 'd')
                                number_txt = td[16].text
                                number_txt = number_txt.replace(",", "")
                                number = int(number_txt)
                                report_object.reported_number = number
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                            except Exception as e:
                                custom_log("try->except monthly report - تولید و فروش - " + str(e), 'd')
                        elif table_title_text == "خدماتوفروش":
                            try:
                                custom_log("report url: " + url, 'd')
                                custom_log("category is: " + "خدمات و فروش", 'd')
                                custom_log("reported_number is: " + td[6].text, 'd')
                                number_txt = td[6].text
                                number_txt = number_txt.replace(",", "")
                                number = int(number_txt)
                                report_object.reported_number = number
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                            except Exception as e:
                                custom_log("try->except monthly report - خدمات و فروش - " + str(e), 'd')
                        elif table_title_text == "فرمدرامدهایعملیاتیماهانه":
                            try:
                                custom_log("report url: " + url, 'd')
                                custom_log("category is: " + "فرم درآمدهای عملیاتی ماهانه", 'd')
                                custom_log("reported_number is: " + td[16].text, 'd')
                                number_txt = td[16].text
                                number_txt = number_txt.replace(",", "")
                                number = int(number_txt)
                                report_object.reported_number = number
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                            except Exception as e:
                                custom_log("try->except monthly report - فرم درآمدهای عملیاتی ماهانه - " + str(e), 'd')
                        elif table_title_text == "محصولات":
                            try:
                                custom_log("report url: " + url, 'd')
                                custom_log("category is: " + "محصولات", 'd')
                                custom_log("reported_number is: " + td[16].text, 'd')
                                number_txt = td[16].text
                                number_txt = number_txt.replace(",", "")
                                number = int(number_txt)
                                report_object.reported_number = number
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                            except Exception as e:
                                custom_log("try->except monthly report - محصولات - " + str(e), 'd')
                        else:
                            custom_log("report url: " + url, 'd')
                            custom_log("category is: " + "unknown category", 'd')
                            report_object.is_finished = True
                            report_object.is_acceptable = False
                            report_object.save()
                        driver.quit()
                        break
                    except Exception as e:
                        custom_log(
                            str(e) + "\nthis page has no proper report, for more information check the url below: ",
                            'd')
                        custom_log("report url: " + url, 'd')
                        custom_log("category is: " + "unknown category", 'd')
                        report_object.is_finished = True
                        report_object.is_acceptable = False
                        report_object.save()
                        break
            else:
                custom_log("get_monthly_report_number page in not ok / unknown category", 'd')
                custom_log("this page has no proper report, for more information check the url below: ", 'd')
                custom_log("report url: " + url, 'd')
                custom_log("category is: " + "unknown category", 'd')
                report_object.is_finished = True
                report_object.is_acceptable = False
                report_object.save()
            break
        except NoSuchElementException as noelement:
            custom_log('get_monthly_report_number no such element exception: ' + str(noelement), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        except WebDriverException as driver_exception:
            custom_log('get_monthly_report_number webdriver exception: ' + str(driver_exception), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            raise
        except Exception as e:
            custom_log('get_monthly_report_number other exception: ' + str(e), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            return custom_log(
                "get_monthly_report_number: after reloading had been tried 3 times, this webdriver exceptions still exist",
                'd')
    custom_log('get_monthly_report_number:' + str(report_object) + ' | complete', 'd')
    driver.quit()


def get_seasonal_report_number(report_object):
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    settings = ConfigSetting.objects.filter().latest('id')
    firefox_profile = webdriver.FirefoxProfile()
    if settings.is_proxy_on:
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.http", get_proxy()[0])
        firefox_profile.set_preference("network.proxy.http_port", get_proxy()[1])
        firefox_profile.update_preferences()
        options.profile = firefox_profile
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    webdriver_problem_number_of_reloading = 0
    while True:
        try:
            number_of_reloading_page = 0
            page_is_ok = False
            while True:
                custom_log("get_seasonal_report_number: starting page load", 'd')
                url = report_object.report_link
                driver.get(url)
                custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()), 'd')
                time.sleep(get_time_sleep())
                try:
                    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, "label")))
                    option_ = driver.find_elements(By.TAG_NAME, 'option')
                    for op in option_:
                        op_text = word_simplifier(op.text.strip(), 'without_space')
                        if op_text == "صورتسودوزیان":
                            op.click()
                            break
                    WebDriverWait(driver, 30).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "table-containet")))
                    page_is_ok = True
                    custom_log("get_seasonal_report_number | page_is_ok? : " + "TRUE", 'd')
                    break
                except Exception as e:
                    custom_log("try->except get_seasonal_report_number  label doesnt load\n" + str(e), 'd')
                    custom_log(
                        "get_seasonal_report_number: page loading problem, 30 second passed and nothing happened",
                        'd')
                number_of_reloading_page += 1
                if number_of_reloading_page == 3:
                    driver.quit()
                    return custom_log(
                        "get_seasonal_report_number: after reloading had been tried 3 times, this page has not been received and passed",
                        'd')
            custom_log("try->except get_seasonal_report_number table_holder class not exist\n", 'd')
            report_time_period = None
            first_td = None
            second_td = None
            gross_profit_and_loss = None
            operating_income = None
            if page_is_ok:
                try:
                    custom_log("get_seasonal_report_number url : \n" + str(url), 'd')
                    try:
                        pass_if_exist = driver.find_element(By.CLASS_NAME, "table_holder")
                        custom_log(pass_if_exist.text.strip(), 'd')
                    except Exception as e:
                        try:
                            symbol_and_name = driver.find_element(By.CLASS_NAME, "symbol_and_name")
                            report_time_period = symbol_and_name.find_element(By.ID, 'ctl00_lblPeriod')
                            report_time_period = report_time_period.text.strip()
                            report_time_period = word_simplifier(report_time_period, 'without_space')
                            if report_time_period.find('3ماهه') != -1:
                                report_time_period = '3 ماهه'
                            elif report_time_period.find('6ماهه') != -1:
                                report_time_period = '6 ماهه'
                            elif report_time_period.find('9ماهه') != -1:
                                report_time_period = '9 ماهه'
                            elif report_time_period.find('12ماهه') != -1:
                                report_time_period = '12 ماهه'
                            else:
                                report_time_period = None

                            custom_log('try-> symbol_and_name. time period: ' + report_time_period, 'd')
                        except Exception as e:
                            custom_log("try->except symbol_and_name cant find time period\n" + str(e), 'd')

                        tds = driver.find_elements(By.TAG_NAME, "td")
                        n = 0
                        for td in tds:
                            if str(td.get_attribute('hidden')) == 'None':
                                spans = td.find_elements(By.TAG_NAME, "span")
                                m = 0
                                for span in spans:
                                    span_text = word_simplifier(span.text, 'without_space')
                                    if span_text == "درامدحقبیمهناخالص":
                                        custom_log("get_seasonal_report_number is درآمد حق بیمه ناخالص", 'd')
                                        m = 1
                                        break
                                    else:
                                        if span_text == "سودزیانخالص":
                                            first_td = tds[n + 1].text
                                            first_td = number_handler(first_td)
                                            second_td = tds[n + 2].text
                                            if second_td == '':
                                                second_td = tds[n + 3].text
                                                if second_td == '':
                                                    second_td = tds[n + 4].text
                                                    if second_td == '':
                                                        second_td = tds[n + 5].text
                                            second_td = number_handler(second_td)
                                            first_td = string_number_to_int(first_td)
                                            second_td = string_number_to_int(second_td)
                                            custom_log('first number: ' + str(first_td))
                                            custom_log('second number: ' + str(second_td))
                                        if span_text == "درامدهایعملیاتی":
                                            operating_income = number_handler(tds[n + 1].text.strip())
                                            operating_income = string_number_to_int(operating_income)
                                            custom_log('operating_income: ' + str(operating_income))
                                        if span_text == "سودزیانناخالص":
                                            gross_profit_and_loss = number_handler(tds[n + 1].text.strip())
                                            gross_profit_and_loss = string_number_to_int(gross_profit_and_loss)
                                            custom_log('gross_profit_and_loss: ' + str(gross_profit_and_loss))
                                if m == 1:
                                    break
                            n += 1
                    try:
                        if float(first_td) > 0 and float(second_td) > 0:
                            if abs(float(first_td)) > abs(float(second_td)):
                                final_number_percentage = (abs(float(first_td) / float(second_td)) - 1) * 100
                                final_number_percentage = round(final_number_percentage)
                                report_object.reported_percentage = final_number_percentage
                                report_object.reported_percentage_color = 'black'
                                report_object.report_time_period = report_time_period
                                report_object.operating_income = operating_income
                                report_object.gross_profit_and_loss = gross_profit_and_loss
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                                custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                            else:
                                final_number_percentage = (abs(float(first_td) / float(second_td)) - 1) * 100
                                final_number_percentage = round(final_number_percentage)
                                report_object.reported_percentage = final_number_percentage
                                report_object.reported_percentage_color = 'black'
                                report_object.report_time_period = report_time_period
                                report_object.operating_income = operating_income
                                report_object.gross_profit_and_loss = gross_profit_and_loss
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                                custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                        elif float(first_td) < 0 and float(second_td) < 0:
                            if abs(float(first_td)) > abs(float(second_td)):
                                final_number_percentage = (abs(float(first_td) / float(second_td)) - 1) * 100
                                final_number_percentage = round(final_number_percentage)
                                report_object.reported_percentage = final_number_percentage * (-1)
                                report_object.reported_percentage_color = 'red'
                                report_object.report_time_period = report_time_period
                                report_object.operating_income = operating_income
                                report_object.gross_profit_and_loss = gross_profit_and_loss
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                                custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                            else:
                                final_number_percentage = (abs(float(first_td) / float(second_td)) - 1) * 100
                                final_number_percentage = round(final_number_percentage) * -1
                                report_object.reported_percentage = final_number_percentage
                                report_object.reported_percentage_color = 'blue'
                                report_object.report_time_period = report_time_period
                                report_object.operating_income = operating_income
                                report_object.gross_profit_and_loss = gross_profit_and_loss
                                report_object.is_finished = True
                                report_object.is_acceptable = True
                                report_object.save()
                                custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                        elif float(first_td) > 0 > float(second_td):
                            final_number_percentage = ((abs(float(first_td) / float(second_td))) + 1) * 100
                            final_number_percentage = round(final_number_percentage)
                            report_object.reported_percentage = final_number_percentage
                            report_object.reported_percentage_color = 'green'
                            report_object.report_time_period = report_time_period
                            report_object.operating_income = operating_income
                            report_object.gross_profit_and_loss = gross_profit_and_loss
                            report_object.is_finished = True
                            report_object.is_acceptable = True
                            report_object.save()
                            custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                        elif float(first_td) < 0 < float(second_td):
                            final_number_percentage = (abs((float(first_td)) / float(second_td)) + 1) * 100
                            final_number_percentage = round(final_number_percentage)
                            report_object.reported_percentage = final_number_percentage
                            report_object.reported_percentage_color = 'red'
                            report_object.report_time_period = report_time_period
                            report_object.operating_income = operating_income
                            report_object.gross_profit_and_loss = gross_profit_and_loss
                            report_object.is_finished = True
                            report_object.is_acceptable = True
                            report_object.save()
                            custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                    except ValueError:
                        custom_log("try->except get_seasonal_report_number value error", 'd')
                        final_number_percentage = "not available"
                        custom_log('درصد گزارش شده: ' + str(final_number_percentage), 'd')
                        report_object.is_finished = True
                        report_object.is_acceptable = False
                        report_object.save()
                    break
                except Exception as e:
                    custom_log("message: " + str(e), 'd')
                    custom_log("this company has no proper report, for more information chek the url below: ", 'd')
                    report_object.is_finished = True
                    report_object.is_acceptable = False
                    report_object.save()
            else:
                custom_log("get_seasonal_report_number: page is not ok", 'd')
                custom_log("this company has no proper report, for more information chek the url below: ", 'd')
                report_object.is_finished = True
                report_object.is_acceptable = False
                report_object.save()
            break
        except NoSuchElementException as noelement:
            custom_log('get_seasonal_report_number no such element exception: ' + str(noelement), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        except WebDriverException as driver_exception:
            custom_log('get_seasonal_report_number webdriver exception: ' + str(driver_exception), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            raise
        except Exception as e:
            custom_log('get_seasonal_report_number other exception: ' + str(e), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            return custom_log(
                "get_seasonal_report_number: after reloading had been tried 3 times, this webdriver exceptions still exist",
                'd')
    custom_log('get_seasonal_report_number:' + str(report_object) + ' | complete', 'd')
    driver.quit()


def check_if_last_page(url):
    options = FirefoxOptions()
    options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    settings = ConfigSetting.objects.filter().latest('id')
    firefox_profile = webdriver.FirefoxProfile()
    if settings.is_proxy_on:
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.http", get_proxy()[0])
        firefox_profile.set_preference("network.proxy.http_port", get_proxy()[1])
        firefox_profile.update_preferences()
        options.profile = firefox_profile
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    webdriver_problem_number_of_reloading = 0
    while True:
        try:
            number_of_reloading_page = 0
            while True:
                custom_log("start check_if_last_page", 'd')
                driver.get(url)
                custom_log("driver.get(url)> url has been fetched. we are waiting for: " + str(get_time_sleep()), 'd')
                time.sleep(get_time_sleep())
                custom_log("spinner start", 'd')
                try:
                    WebDriverWait(driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner")))
                    try:
                        retry_button = driver.find_element(By.XPATH,
                                                           "/html/body/form/div[3]/div[1]/div[1]/div[2]/div[2]/div/div/input")
                        custom_log("loading of page has been failed. error: صفحه لود نشد", 'd')
                        time_sleep = 60
                        custom_log("waiting for: " + str(time_sleep) + "seconds", 'd')
                        time.sleep(time_sleep)
                    except Exception as e:
                        custom_log("page has loaded", 'd')
                        try:
                            app_table = driver.find_element(By.CLASS_NAME, "text-danger")
                            custom_log(app_table.text.strip(), 'd')
                            driver.quit()
                            custom_log("this is last page", 'd')
                            return True
                        except Exception as e:
                            driver.quit()
                            custom_log("this is not last page", 'd')
                            return False
                except Exception as e:
                    custom_log("check_if_last_page: spinner problem, 30 second passed and spinner still spinning", 'd')
                number_of_reloading_page += 1
                if number_of_reloading_page == 3:
                    driver.quit()
                    custom_log(
                        "check_if_last_page: after reloading had been tried 3 times, this page has not been received and passed",
                        'd')
                    return True
        except NoSuchElementException as noelement:
            custom_log('check_if_last_page no such element exception: ' + str(noelement), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        except WebDriverException as driver_exception:
            custom_log('check_if_last_page webdriver exception: ' + str(driver_exception), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        except ConnectionError as e:
            raise
        except Exception as e:
            custom_log('check_if_last_page other exception: ' + str(e), 'd')
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', 'd')
            time.sleep(get_time_sleep())
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            custom_log(
                "check_if_last_page: after reloading had been tried 3 times, this webdriver exceptions still exist",
                'd')
            return True


# ------------ End Scraper functions -------------------


# ------------ Start Calculator Functions -------------------
def monthly_report_calculator(company_profile_object):
    custom_log("---------------- monthly report calculation start------------------\n", 'd')
    company_object = company_profile_object.company
    monthly_report_comparison_1_4 = None
    monthly_report_comparison_2_5 = None
    monthly_report_comparison_3_6 = None
    is_monthly_report_ready = False
    try:
        latest_monthly_report = MonthlyReport.objects.filter(company=company_object).latest('month_reported_date')
        this_year = latest_monthly_report.month_reported_date.year
        this_month = latest_monthly_report.month_reported_date.month
        custom_log("latest monthly report year: " + str(this_year), "d")
        custom_log("latest monthly report month: " + str(this_month), "d")
        x01 = latest_monthly_report.reported_number
        company_profile_object.monthly_report_1_date = latest_monthly_report.month_reported_date
        if this_month == 1:
            try:
                m2 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  12)).latest(
                    'month_reported_date')
                x02 = m2.reported_number
                company_profile_object.monthly_report_2_date = m2.month_reported_date
            except:
                custom_log("مشکل در دریافت گزارش ماه یکی مانده به آخر امسال", "d")
                x02 = 0
            try:
                m3 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  11)).latest(
                    'month_reported_date')
                x03 = m3.reported_number
                company_profile_object.monthly_report_3_date = m3.month_reported_date
            except:
                custom_log("مشکل در دریافت گزارش ماه دوتا مانده به آخر امسال", "d")
                x03 = 0
            try:
                m4 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  1)).latest(
                    'month_reported_date')
                x04 = m4.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه آخر سال قبل", "d")
                x04 = 0
            try:
                m5 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 2,
                                                                                                  12)).latest(
                    'month_reported_date')
                x05 = m5.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه یکی مانده به آخر سال قبل", "d")
                x05 = 0
            try:
                m6 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 2,
                                                                                                  11)).latest(
                    'month_reported_date')
                x06 = m6.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه دوتا مانده به آخر سال قبل", "d")
                x06 = 0
        elif this_month == 2:
            try:
                m2 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year,
                                                                                                  1)).latest(
                    'month_reported_date')
                x02 = m2.reported_number
                company_profile_object.monthly_report_2_date = m2.month_reported_date
            except:
                custom_log("مشکل در دریافت گزارش ماه یکی مانده به آخر امسال", "d")
                x02 = 0
            try:
                m3 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  12)).latest(
                    'month_reported_date')
                x03 = m3.reported_number
                company_profile_object.monthly_report_3_date = m3.month_reported_date
            except:
                custom_log("مشکل در دریافت گزارش ماه دوتا مانده به آخر امسال", "d")
                x03 = 0
            try:
                m4 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  2)).latest(
                    'month_reported_date')
                x04 = m4.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه آخر سال قبل", "d")
                x04 = 0
            try:
                m5 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  1)).latest(
                    'month_reported_date')
                x05 = m5.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه یکی مانده به آخر سال قبل", "d")
                x05 = 0
            try:
                m6 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 2,
                                                                                                  12)).latest(
                    'month_reported_date')
                x06 = m6.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه دوتا مانده به آخر سال قبل", "d")
                x06 = 0
        else:
            try:
                m2 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year,
                                                                                                  this_month - 1)).latest(
                    'month_reported_date')
                x02 = m2.reported_number
                company_profile_object.monthly_report_2_date = m2.month_reported_date
            except:
                custom_log("مشکل در دریافت گزارش ماه یکی مانده به آخر امسال", "d")
                x02 = 0
            try:
                m3 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year,
                                                                                                  this_month - 2)).latest(
                    'month_reported_date')
                x03 = m3.reported_number
                company_profile_object.monthly_report_3_date = m3.month_reported_date
            except:
                custom_log("مشکل در دریافت گزارش ماه دوتا مانده به آخر امسال", "d")
                x03 = 0
            try:
                m4 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  this_month)).latest(
                    'month_reported_date')
                x04 = m4.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه آخر سال قبل", "d")
                x04 = 0
            try:
                m5 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  this_month - 1)).latest(
                    'month_reported_date')
                x05 = m5.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه یکی مانده به آخر سال قبل", "d")
                x05 = 0
            try:
                m6 = MonthlyReport.objects.filter(company=company_object,
                                                  month_reported_date__range=date_range_generator(this_year - 1,
                                                                                                  this_month - 2)).latest(
                    'month_reported_date')
                x06 = m6.reported_number
            except:
                custom_log("مشکل در دریافت گزارش ماه دوتا مانده به آخر سال قبل", "d")
                x06 = 0
        try:
            c1 = ((x01 / x04) - 1) * 100
            c1 = round(c1, 2)
            custom_log("c1: " + str(c1), "d")
            monthly_report_comparison_1_4 = c1
        except Exception as e:
            custom_log("c1 cant calculate because: " + str(e), "d")
        try:
            c2 = ((x02 / x05) - 1) * 100
            c2 = round(c2, 2)
            custom_log("c2: " + str(c2), "d")
            monthly_report_comparison_2_5 = c2
        except Exception as e:
            custom_log("c2 cant calculate because: " + str(e), "d")
        try:
            c3 = ((x03 / x06) - 1) * 100
            c3 = round(c3, 2)
            custom_log("c3: " + str(c3), "d")
            monthly_report_comparison_3_6 = c3
        except Exception as e:
            custom_log("c3 cant calculate because: " + str(e), "d")
        if monthly_report_comparison_1_4 is None:
            custom_log("monthly report comparison 1_4: None ", "d")
        else:
            custom_log("monthly report comparison 1_4: " + str(monthly_report_comparison_1_4), "d")

        if monthly_report_comparison_2_5 is None:
            custom_log("monthly report comparison 2_5: None ", "d")
        else:
            custom_log("monthly report comparison 2_5: " + str(monthly_report_comparison_2_5), "d")

        if monthly_report_comparison_3_6 is None:
            custom_log("monthly report comparison 3_6: None ", "d")
        else:
            custom_log("monthly report comparison 3_6: " + str(monthly_report_comparison_3_6), "d")

        if monthly_report_comparison_1_4 and monthly_report_comparison_2_5 and monthly_report_comparison_3_6 is not None:
            is_monthly_report_ready = True
            custom_log("is all report ok?: " + "True", "d")
        else:
            is_monthly_report_ready = False
            custom_log("is all report ok?: " + "False", "d")
    except Exception as e:
        custom_log("this is monthly main exception: " + str(e), "d")

    company_profile_object.monthly_report_comparison_1_4 = monthly_report_comparison_1_4
    company_profile_object.monthly_report_comparison_2_5 = monthly_report_comparison_2_5
    company_profile_object.monthly_report_comparison_3_6 = monthly_report_comparison_3_6
    company_profile_object.is_monthly_report_ready = is_monthly_report_ready
    company_profile_object.save()
    custom_log("---------------- monthly report calculation end------------------\n", 'd')


def seasonal_report_calculator(company_profile_object):
    custom_log("---------------- seasonal report calculation starts ------------------\n", 'd')
    company_object = company_profile_object.company
    latest_seasonal_report = SeasonalReport.objects.filter(company=company_object).latest('season_reported_date')
    this_year = latest_seasonal_report.season_reported_date.year
    custom_log("latest seasonal report year: " + str(this_year), "d")
    this_month = latest_seasonal_report.season_reported_date.month
    custom_log("latest seasonal report month: " + str(this_month), "d")

    if this_month == 1 or this_month == 2 or this_month == 3:
        # spring
        spring_report = latest_seasonal_report
        company_profile_object.seasonal_report_spring_date_order = 1

        # summer
        summer_date_range_from = jdatetime.date(year=(this_year - 1), month=4, day=1)
        summer_date_range_to = jdatetime.date(year=(this_year - 1), month=6, day=31)
        summer_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[summer_date_range_from,
                                                                                   summer_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_summer_date_order = 4

        # fall
        fall_date_range_from = jdatetime.date(year=(this_year - 1), month=7, day=1)
        fall_date_range_to = jdatetime.date(year=(this_year - 1), month=9, day=30)
        fall_report = SeasonalReport.objects.filter(company=company_object,
                                                    season_reported_date__range=[fall_date_range_from,
                                                                                 fall_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_fall_date_order = 3

        # winter
        winter_date_range_from = jdatetime.date(year=(this_year - 1), month=10, day=1)
        winter_date_range_to = jdatetime.date(year=(this_year - 1), month=12, day=30)
        winter_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[winter_date_range_from,
                                                                                   winter_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_winter_date_order = 2
    elif this_month == 4 or this_month == 5 or this_month == 6:
        # spring
        spring_date_range_from = jdatetime.date(year=this_year, month=1, day=1)
        spring_date_range_to = jdatetime.date(year=this_year, month=3, day=31)
        spring_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[spring_date_range_from,
                                                                                   spring_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_spring_date_order = 2

        # summer
        summer_report = latest_seasonal_report
        company_profile_object.seasonal_report_summer_date_order = 1

        # fall
        fall_date_range_from = jdatetime.date(year=(this_year - 1), month=7, day=1)
        fall_date_range_to = jdatetime.date(year=(this_year - 1), month=9, day=30)
        fall_report = SeasonalReport.objects.filter(company=company_object,
                                                    season_reported_date__range=[fall_date_range_from,
                                                                                 fall_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_fall_date_order = 4

        # winter
        winter_date_range_from = jdatetime.date(year=(this_year - 1), month=10, day=1)
        winter_date_range_to = jdatetime.date(year=(this_year - 1), month=12, day=30)
        winter_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[winter_date_range_from,
                                                                                   winter_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_winter_date_order = 3
    elif this_month == 7 or this_month == 8 or this_month == 9:
        # spring
        spring_date_range_from = jdatetime.date(year=this_year, month=1, day=1)
        spring_date_range_to = jdatetime.date(year=this_year, month=3, day=31)
        spring_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[spring_date_range_from,
                                                                                   spring_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_spring_date_order = 3

        # summer
        summer_date_range_from = jdatetime.date(year=this_year, month=4, day=1)
        summer_date_range_to = jdatetime.date(year=this_year, month=6, day=31)
        summer_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[summer_date_range_from,
                                                                                   summer_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_summer_date_order = 2

        # fall
        fall_report = latest_seasonal_report
        company_profile_object.seasonal_report_fall_date_order = 1

        # winter
        winter_date_range_from = jdatetime.date(year=(this_year - 1), month=10, day=1)
        winter_date_range_to = jdatetime.date(year=(this_year - 1), month=12, day=30)
        winter_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[winter_date_range_from,
                                                                                   winter_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_winter_date_order = 4
    else:
        # spring
        spring_date_range_from = jdatetime.date(year=this_year, month=1, day=1)
        spring_date_range_to = jdatetime.date(year=this_year, month=3, day=31)
        spring_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[spring_date_range_from,
                                                                                   spring_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_spring_date_order = 4

        # summer
        summer_date_range_from = jdatetime.date(year=this_year, month=4, day=1)
        summer_date_range_to = jdatetime.date(year=this_year, month=6, day=31)
        summer_report = SeasonalReport.objects.filter(company=company_object,
                                                      season_reported_date__range=[summer_date_range_from,
                                                                                   summer_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_summer_date_order = 3

        # fall
        fall_date_range_from = jdatetime.date(year=this_year, month=7, day=1)
        fall_date_range_to = jdatetime.date(year=this_year, month=9, day=30)
        fall_report = SeasonalReport.objects.filter(company=company_object,
                                                    season_reported_date__range=[fall_date_range_from,
                                                                                 fall_date_range_to]).latest(
            'season_reported_date')
        company_profile_object.seasonal_report_fall_date_order = 2

        # winter
        winter_report = latest_seasonal_report
        company_profile_object.seasonal_report_winter_date_order = 1

    # spring
    seasonal_report_spring_percentage = spring_report.reported_percentage
    seasonal_report_spring_color = spring_report.reported_percentage_color
    seasonal_report_spring_date = spring_report.season_reported_date
    custom_log("seasonal report spring date: " + str(seasonal_report_spring_date), "d")
    custom_log("seasonal report spring percentage: " + str(seasonal_report_spring_percentage), "d")
    custom_log("seasonal report spring color: " + str(seasonal_report_spring_color), "d")

    # summer
    seasonal_report_summer_percentage = summer_report.reported_percentage
    seasonal_report_summer_color = summer_report.reported_percentage_color
    seasonal_report_summer_date = summer_report.season_reported_date
    custom_log("seasonal report summer date: " + str(seasonal_report_summer_date), "d")
    custom_log("seasonal report summer percentage: " + str(seasonal_report_summer_percentage), "d")
    custom_log("seasonal report summer color: " + str(seasonal_report_summer_color), "d")

    # fall
    seasonal_report_fall_percentage = fall_report.reported_percentage
    seasonal_report_fall_color = fall_report.reported_percentage_color
    seasonal_report_fall_date = fall_report.season_reported_date
    custom_log("seasonal report fall date: " + str(seasonal_report_fall_date), "d")
    custom_log("seasonal report fall percentage: " + str(seasonal_report_fall_percentage), "d")
    custom_log("seasonal report fall color: " + str(seasonal_report_fall_color), "d")

    # winter
    seasonal_report_winter_percentage = winter_report.reported_percentage
    seasonal_report_winter_color = winter_report.reported_percentage_color
    seasonal_report_winter_date = winter_report.season_reported_date
    custom_log("seasonal report winter date: " + str(seasonal_report_winter_date), "d")
    custom_log("seasonal report winter percentage: " + str(seasonal_report_winter_percentage), "d")
    custom_log("seasonal report winter color: " + str(seasonal_report_winter_color), "d")

    company_profile_object.seasonal_report_spring_percentage = seasonal_report_spring_percentage
    company_profile_object.seasonal_report_spring_color = seasonal_report_spring_color
    company_profile_object.seasonal_report_spring_date = seasonal_report_spring_date

    company_profile_object.seasonal_report_summer_percentage = seasonal_report_summer_percentage
    company_profile_object.seasonal_report_summer_color = seasonal_report_summer_color
    company_profile_object.seasonal_report_summer_date = seasonal_report_summer_date

    company_profile_object.seasonal_report_fall_percentage = seasonal_report_fall_percentage
    company_profile_object.seasonal_report_fall_color = seasonal_report_fall_color
    company_profile_object.seasonal_report_fall_date = seasonal_report_fall_date

    company_profile_object.seasonal_report_winter_percentage = seasonal_report_winter_percentage
    company_profile_object.seasonal_report_winter_color = seasonal_report_winter_color
    company_profile_object.seasonal_report_winter_date = seasonal_report_winter_date

    if seasonal_report_spring_percentage is not None or seasonal_report_summer_percentage is not None \
            or seasonal_report_fall_percentage is not None or seasonal_report_winter_percentage is not None:
        company_profile_object.is_seasonal_report_ready = True
    company_profile_object.save()
    custom_log("---------------- seasonal report calculation ends ------------------\n", 'd')


def seasonal_report_operating_ratio_calculator(company_profile_object):
    custom_log("---------------- seasonal report operating ratio calculator starts ------------------\n", 'd')
    company = company_profile_object.company
    seasonal_reports = SeasonalReport.objects.filter(company=company)
    three_month_reports = []
    for report in seasonal_reports:
        if report.report_time_period == '3 ماهه':
            three_month_reports.append(report)
            report.operating_ratio = int(round(((report.gross_profit_and_loss / report.operating_income) * 100), 0))
            report.save()
    custom_log("three_month_reports: " + str(three_month_reports), 'd')

    for report in seasonal_reports:
        if report.report_time_period != '3 ماهه':
            for three_month_report in three_month_reports:
                if report.season_reported_date.year == three_month_report.season_reported_date.year:
                    report.operating_ratio = int(
                        round((((report.gross_profit_and_loss - three_month_report.gross_profit_and_loss) / (
                                report.operating_income - three_month_report.operating_income)) * 100), 0))
                    report.save()
                    custom_log("report company name: " + str(report.report_title) + ' report date: ' + str(report.season_reported_date), 'd')
                    custom_log("source three_month_report: " + str(three_month_report.season_reported_date), 'd')
                    break
            custom_log('--------')
    custom_log("---------------- seasonal report operating ratio calculator ends ------------------\n", 'd')


# ------------ End Calculator Functions -------------------


# ------------ Start Helper Functions -------------------
def codal_first_page():
    url = "https://www.codal.ir/ReportList.aspx?search&LetterType=-1&FromDate=1400%2F01%2F01&AuditorRef=-1&PageNumber=1&Audited&NotAudited&IsNotAudited=false&Childs=false&Mains&Publisher=false&CompanyState=-1&Category=-1&CompanyType=1&Consolidatable&NotConsolidatable"
    return url


def codal_monthly_report_page(company_link, n):
    url = str(company_link) + "&LetterType=-1&FromDate=1400%2F01%2F01&AuditorRef=-1&PageNumber=" + str(
        n) + "&Audited&NotAudited&IsNotAudited=false&Childs=false&Mains&Publisher=false&CompanyState=-1&Category=3&CompanyType=-1&Consolidatable&NotConsolidatable"
    return url


def codal_seasonal_report_page(company_link, n):
    url = str(company_link) + "&LetterType=6&FromDate=1400%2F01%2F01&AuditorRef=-1&PageNumber=" + str(
        n) + "&Audited&NotAudited&IsNotAudited=false&Childs=false&Mains&Publisher=false&CompanyState=-1&Category=1&CompanyType=-1&Consolidatable&NotConsolidatable"
    return url


def number_handler(string):
    string = string.replace(",", "")
    if string.find("(") != -1:
        string = string.replace("(", "-")
        string = string.replace(")", "")
    return string


def string_number_to_int(string: str):
    if str(string).find('-') != -1:
        string = string.replace('-', '')
        string = -1 * int(string)
    else:
        string = int(string)
    return string
# ------------ End Helper Functions -------------------
