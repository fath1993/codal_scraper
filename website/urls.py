from django.urls import path

from website.views import index, report_view

app_name = 'website'

urlpatterns = [
    path('', index, name='landing-page'),
    path('<str:report_tag>/', report_view, name='report-view'),
]
