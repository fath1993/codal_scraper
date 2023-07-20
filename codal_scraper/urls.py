from django.contrib import admin
from django.urls import path, include
from website.views import report_view_1, report_view_2, report_view_3, report_view_4
from codal.views import robot
from django.conf.urls.static import static
from django.conf import settings

app_name = 'codal-scraper'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('website.urls')),
    path('0/', report_view_1),
    path('1/', report_view_2),
    path('2/', report_view_3),
    path('33/', report_view_4),
    path('robot/<str:ck>/', robot),
    path('logs/', include('custom_logs.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)