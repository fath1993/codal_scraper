import jdatetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from custom_logs.models import custom_log
from django_jalali.db import models as jmodel


class CompanyLink(models.Model):
    badge = models.CharField(null=False, blank=False, max_length=255, verbose_name="نماد")
    link = models.CharField(max_length=2000, null=False, blank=False, verbose_name="لینک")

    def __str__(self):
        return self.badge + ' | ' + self.link

    class Meta:
        ordering = ['badge', ]
        verbose_name = "لینک شرکت"
        verbose_name_plural = "لینک شرکت ها"


class Company(models.Model):
    badge = models.CharField(max_length=255, null=True, blank=True, verbose_name="نماد سازمان")
    link = models.CharField(max_length=2000, null=True, blank=True, verbose_name="لینک جزئیات سازمان")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="نام سازمان")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ و زمان بروزرسانی")

    class Meta:
        ordering = ['-updated_at', ]
        verbose_name = "شرکت"
        verbose_name_plural = "شرکت ها"

    def __str__(self):
        return self.badge


class CompanyProfile(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, null=False, blank=False, verbose_name="شرکت")

    is_monthly_report_ready = models.BooleanField(default=False,
                                                  verbose_name="آیا برای این شرکت گزارشات ماهانه قابل ارائه است؟")
    is_seasonal_report_ready = models.BooleanField(default=False,
                                                   verbose_name="آیا برای این شرکت گزارشات فصلی قابل ارائه است؟")
    monthly_report_1_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                              verbose_name="تاریخ آخرین گزارش ماهانه موجود")
    monthly_report_2_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                              verbose_name="تاریخ گزارش ماهانه یکی مانده به آخر")
    monthly_report_3_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                              verbose_name="تاریخ گزارش ماهانه دوتا مانده به آخر")
    monthly_report_comparison_1_4 = models.FloatField(null=True, blank=True, editable=False,
                                                      verbose_name="مقایسه آخرین گزارش ماهانه موجود")
    monthly_report_comparison_2_5 = models.FloatField(null=True, blank=True, editable=False,
                                                      verbose_name="مقایسه گزارش ماهانه یکی مانده به آخر")
    monthly_report_comparison_3_6 = models.FloatField(null=True, blank=True, editable=False,
                                                      verbose_name="مقایسه گزارش ماهانه دوتا مانده به آخر")
    seasonal_report_spring_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                                    verbose_name="تاریخ گزارش فصلی بهار")
    seasonal_report_spring_date_order = models.SmallIntegerField(null=True, blank=True, editable=False, default=1)
    seasonal_report_spring_percentage = models.FloatField(null=True, blank=True, editable=False,
                                                          verbose_name="درصد گزارش فصلی بهار")
    seasonal_report_spring_color = models.CharField(max_length=255, null=True, blank=True, editable=False,
                                                    verbose_name="رنگ گزارش فصلی بهار")
    seasonal_report_spring_operating_ratio = models.IntegerField(null=True, blank=True, editable=False, verbose_name="عدد عملیاتی فصل بهار")
    seasonal_report_summer_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                                    verbose_name="تاریخ گزارش فصلی تابستان")
    seasonal_report_summer_date_order = models.SmallIntegerField(null=True, blank=True, editable=False, default=2)
    seasonal_report_summer_percentage = models.FloatField(null=True, blank=True, editable=False,
                                                          verbose_name="درصد گزارش فصلی تابستان")
    seasonal_report_summer_color = models.CharField(max_length=255, null=True, blank=True, editable=False,
                                                    verbose_name="رنگ گزارش فصلی تابستان")
    seasonal_report_summer_operating_ratio = models.IntegerField(null=True, blank=True, editable=False,
                                                                 verbose_name="عدد عملیاتی فصل تابستان")
    seasonal_report_fall_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                                  verbose_name="تاریخ گزارش فصلی پاییز")
    seasonal_report_fall_date_order = models.SmallIntegerField(null=True, blank=True, editable=False, default=3)
    seasonal_report_fall_percentage = models.FloatField(null=True, blank=True, editable=False,
                                                        verbose_name="درصد گزارش فصلی پاییز")
    seasonal_report_fall_color = models.CharField(max_length=255, null=True, blank=True, editable=False,
                                                  verbose_name="رنگ گزارش فصلی پاییز")
    seasonal_report_fall_operating_ratio = models.IntegerField(null=True, blank=True, editable=False,
                                                                 verbose_name="عدد عملیاتی فصل پاییز")
    seasonal_report_winter_date = jmodel.jDateField(null=True, blank=True, editable=False,
                                                    verbose_name="تاریخ گزارش فصلی زمستان")
    seasonal_report_winter_date_order = models.SmallIntegerField(null=True, blank=True, editable=False, default=4)
    seasonal_report_winter_percentage = models.FloatField(null=True, blank=True, editable=False,
                                                          verbose_name="درصد گزارش فصلی زمستان")
    seasonal_report_winter_color = models.CharField(max_length=255, null=True, blank=True, editable=False,
                                                    verbose_name="رنگ گزارش فصلی زمستان")
    seasonal_report_winter_operating_ratio = models.IntegerField(null=True, blank=True, editable=False,
                                                                 verbose_name="عدد عملیاتی فصل زمستان")

    class Meta:
        verbose_name = "پروفایل شرکت"
        verbose_name_plural = "پروفایل شرکت ها"

    def __str__(self):
        return self.company.badge + ' | ' + self.company.name


@receiver(post_save, sender=Company)
def company_profile_creator(sender, instance, **kwargs):
    try:
        profile = CompanyProfile.objects.get(company=instance)
    except:
        new_company_profile = CompanyProfile(
            company=instance
        )
        new_company_profile.save()


class MonthlyReport(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False, verbose_name="شرکت")
    report_title = models.CharField(max_length=255, null=False, blank=False, verbose_name="موضوع گزارش")
    report_link = models.CharField(max_length=2000, null=True, blank=True, verbose_name="لینک گزارش")
    report_status = models.CharField(max_length=255, null=True, blank=True, verbose_name="وضعیت گزارش")
    reported_number = models.IntegerField(null=True, blank=True, verbose_name="عدد گزارش")
    month_reported_date = jmodel.jDateField(null=False, blank=False,
                                            verbose_name="گزارش فعالیت ماهانه دوره ۱ ماهه منتهی به تاریخ")
    report_has_sent_at = jmodel.jDateTimeField(null=False, blank=False,
                                               verbose_name="تاریخ و زمان ارسال گزارش توسط کدال")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ و زمان بروزرسانی")
    is_finished = models.BooleanField(default=False, verbose_name="آیا این گزارش کامل شده است؟")
    is_acceptable = models.BooleanField(default=False, verbose_name="آیا این گزارش با فرمت های طراحی شده سازگار است؟")

    class Meta:
        ordering = ['-month_reported_date', ]
        verbose_name = "گزارش ماهانه"
        verbose_name_plural = "گزارشات ماهانه"

    def __str__(self):
        return str(self.company.badge)


class SeasonalReport(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False, verbose_name="شرکت")
    report_title = models.CharField(max_length=255, null=False, blank=False, verbose_name="موضوع گزارش")
    report_link = models.CharField(max_length=2000, null=True, blank=True, verbose_name="لینک گزارش")
    report_time_period = models.CharField(max_length=255, null=True, blank=True, verbose_name="گزارش چند ماهه")
    report_status = models.CharField(max_length=255, null=True, blank=True, verbose_name="وضعیت گزارش")
    reported_percentage = models.FloatField(max_length=255, null=True, blank=True, verbose_name="درصد گزارش شده")
    reported_percentage_color = models.CharField(max_length=255, null=True, blank=True, verbose_name="رنگ درصد")
    operating_income = models.FloatField(max_length=255, null=True, blank=True, verbose_name="درآمد های عملیاتی")
    gross_profit_and_loss = models.FloatField(max_length=255, null=True, blank=True, verbose_name="سود و زیان ناخالص")
    operating_ratio = models.FloatField(max_length=255, null=True, blank=True,
                                        verbose_name="تقسیم درآمد های عملیاتی بر سود یا زیان ناخالص")
    season_reported_date = jmodel.jDateField(null=False, blank=False, verbose_name="گزارش فصلی چند ماهه منتهی به تاریخ")
    report_has_sent_at = jmodel.jDateTimeField(null=False, blank=False,
                                               verbose_name="تاریخ و زمان ارسال گزارش توسط کدال")
    created_at = jmodel.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")
    updated_at = jmodel.jDateTimeField(auto_now=True, verbose_name="تاریخ و زمان بروزرسانی")
    is_finished = models.BooleanField(default=False, verbose_name="آیا این گزارش کامل شده است؟")
    is_acceptable = models.BooleanField(default=False, verbose_name="آیا این گزارش با فرمت های طراحی شده سازگار است؟")

    class Meta:
        ordering = ['-season_reported_date', ]
        verbose_name = "گزارش فصلی"
        verbose_name_plural = "گزارش فصلی"

    def __str__(self):
        return str(self.company.badge)


class ConfigSetting(models.Model):
    sleep_time = models.PositiveSmallIntegerField(default=60, verbose_name="زمان توقف ربات بین هر کوئری")
    is_proxy_on = models.BooleanField(default=True, null=False, blank=False, verbose_name='پراکسی فعال باشد؟')

    def __str__(self):
        return str(": زمان تعیین شده") + str(self.sleep_time)

    class Meta:
        verbose_name = "تنظیمات"
        verbose_name_plural = "تنظیمات"


def config_settings():
    try:
        codal_scraper_settings = ConfigSetting.objects.filter().latest('id')
    except:
        codal_scraper_settings = ConfigSetting(
            sleep_time=40,
            is_proxy_on=False,
        )
        codal_scraper_settings.save()
    return codal_scraper_settings
