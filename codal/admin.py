from django.contrib import admin
from codal.models import Company, MonthlyReport, SeasonalReport, CompanyLink, ConfigSetting, CompanyProfile


@admin.register(CompanyLink)
class CompaniesAdmin(admin.ModelAdmin):
    list_display = (
        'badge',
        'link',
    )
    search_fields = (
        'badge',
    )
    fields = (
        'badge',
        'link',
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'badge',
        'link',
        'name',
        'created_at_display',
        'updated_at_display',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    search_fields = (
        'badge',
        'name',
    )

    fields = (
        'badge',
        'link',
        'name',
        'created_at',
        'updated_at',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        created_at = obj.created_at.strftime('%Y-%m-%d %H:%M')
        return created_at

    @admin.display(description='تاریخ بروز رسانی', empty_value='???')
    def updated_at_display(self, obj):
        created_at = obj.created_at.strftime('%Y-%m-%d %H:%M')
        return created_at


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'is_monthly_report_ready',
        'is_seasonal_report_ready',
    )

    readonly_fields = (
        'monthly_report_1_date',
        'monthly_report_2_date',
        'monthly_report_3_date',
        'monthly_report_comparison_1_4',
        'monthly_report_comparison_2_5',
        'monthly_report_comparison_3_6',
        'seasonal_report_spring_date',
        'seasonal_report_spring_date_order',
        'seasonal_report_spring_percentage',
        'seasonal_report_spring_color',
        'seasonal_report_summer_date',
        'seasonal_report_summer_date_order',
        'seasonal_report_summer_percentage',
        'seasonal_report_summer_color',
        'seasonal_report_fall_date',
        'seasonal_report_fall_date_order',
        'seasonal_report_fall_percentage',
        'seasonal_report_fall_color',
        'seasonal_report_winter_date',
        'seasonal_report_winter_date_order',
        'seasonal_report_winter_percentage',
        'seasonal_report_winter_color',
    )

    search_fields = (
        'company',
    )

    fields = (
        'company',
        'is_monthly_report_ready',
        'is_seasonal_report_ready',
        'monthly_report_1_date',
        'monthly_report_2_date',
        'monthly_report_3_date',
        'monthly_report_comparison_1_4',
        'monthly_report_comparison_2_5',
        'monthly_report_comparison_3_6',
        'seasonal_report_spring_date',
        'seasonal_report_spring_date_order',
        'seasonal_report_spring_percentage',
        'seasonal_report_spring_color',
        'seasonal_report_summer_date',
        'seasonal_report_summer_date_order',
        'seasonal_report_summer_percentage',
        'seasonal_report_summer_color',
        'seasonal_report_fall_date',
        'seasonal_report_fall_date_order',
        'seasonal_report_fall_percentage',
        'seasonal_report_fall_color',
        'seasonal_report_winter_date',
        'seasonal_report_winter_date_order',
        'seasonal_report_winter_percentage',
        'seasonal_report_winter_color',
    )

    @admin.display(description='تاریخ ایجاد', empty_value='???')
    def created_at_display(self, obj):
        created_at = obj.created_at.strftime('%Y-%m-%d %H:%M')
        return created_at

    @admin.display(description='تاریخ بروز رسانی', empty_value='???')
    def updated_at_display(self, obj):
        created_at = obj.created_at.strftime('%Y-%m-%d %H:%M')
        return created_at


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'report_title',
        'report_status',
        'reported_number',
        'month_reported_date',
        'report_has_sent_at_display',
        'is_finished',
        'is_acceptable',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    search_fields = (
        'company',
        'report_title',
    )

    list_filter = (
        'is_finished',
        'is_acceptable',
    )

    fields = (
        'company',
        'report_title',
        'report_link',
        'report_status',
        'reported_number',
        'month_reported_date',
        'report_has_sent_at',
        'created_at',
        'updated_at',
        'is_finished',
        'is_acceptable',
    )

    @admin.display(description='تاریخ انتشار توسط کدال', empty_value='???')
    def report_has_sent_at_display(self, obj):
        report_has_sent_at = obj.report_has_sent_at.strftime('%Y-%m-%d %H:%M')
        return report_has_sent_at


@admin.register(SeasonalReport)
class SeasonalReportAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'report_title',
        'report_status',
        'report_time_period',
        'season_reported_date',
        'report_has_sent_at_display',
        'is_finished',
        'is_acceptable',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    search_fields = (
        'company',
        'report_title',
    )

    list_filter = (
        'is_finished',
        'is_acceptable',
    )

    fields = (
        'company',
        'report_title',
        'report_link',
        'report_status',
        'report_time_period',
        'reported_percentage',
        'reported_percentage_color',
        'operating_income',
        'gross_profit_and_loss',
        'operating_ratio',
        'season_reported_date',
        'report_has_sent_at',
        'created_at',
        'updated_at',
        'is_finished',
        'is_acceptable',
    )

    @admin.display(description='تاریخ انتشار توسط کدال', empty_value='???')
    def report_has_sent_at_display(self, obj):
        report_has_sent_at = obj.report_has_sent_at.strftime('%Y-%m-%d %H:%M')
        return report_has_sent_at


@admin.register(ConfigSetting)
class Admin(admin.ModelAdmin):
    list_display = (
        'sleep_time',
        'is_proxy_on',
    )

    fields = (
        'sleep_time',
        'is_proxy_on',
    )

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)