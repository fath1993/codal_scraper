from django.urls import path

from website.views import report_spring, report_winter, report_fall, report_summer, index

app_name = 'website'

urlpatterns = [
    path('', index, name='landing-page'),
    path('3/', report_spring, name='report-spring'),
    path('6/', report_summer, name='report-summer'),
    path('9/', report_fall, name='report-fall'),
    path('12/', report_winter, name='report-winter'),
]
