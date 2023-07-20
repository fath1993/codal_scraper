from django.contrib import admin
from proxies.models import Proxy


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = (
        'proxy_ip',
        'proxy_port',
        'is_working',
    )
    readonly_fields = (
        'is_working',
        'response_text',
    )
    fields = (
        'proxy_ip',
        'proxy_port',
        'is_working',
        'response_text',
    )
