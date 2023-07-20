import requests
from django.db import models
from latest_user_agents import get_random_user_agent
from codal.models import Company, MonthlyReport, SeasonalReport, ConfigSetting
import time
from custom_logs.models import custom_log


class Proxy(models.Model):
    proxy_ip = models.CharField(max_length=30, null=False, blank=False, verbose_name="proxy ip")
    proxy_port = models.CharField(max_length=30, null=False, blank=False, verbose_name="proxy port")
    is_working = models.BooleanField(default=False, editable=False, verbose_name="آیا پراکسی فعال است؟")
    response_text = models.TextField(default="-", editable=False, verbose_name="داده های دریافت شده توسط پراکسی")

    def __str__(self):
        return "proxy: " + self.proxy_ip + ":" + self.proxy_port

    class Meta:
        verbose_name = "پروکسی"
        verbose_name_plural = "پروکسی ها"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        res = check_proxy_availability(get_proxy())
        if res[0]:
            self.is_working = True
        else:
            self.is_working = False
        self.response_text = res[1]
        super().save(*args, **kwargs)


def get_proxy():
    proxy = Proxy.objects.filter().latest('id')
    return str(proxy.proxy_ip), str(proxy.proxy_port)


headers = {
    'user-agent': get_random_user_agent(),
}


def check_proxy_availability(proxy: tuple):
    settings = ConfigSetting.objects.filter().latest('id')
    if not settings.is_proxy_on:
        res = 'proxy is off'
        return True, res
    custom_log("checking proxy " + str(proxy) + "...", 'd')
    url = "https://www.codal.ir"
    try:
        custom_log("waiting 2 second", 'd')
        time.sleep(2)
        custom_log("start check proxy availability", 'd')
        r = requests.get(url, headers=headers, proxies={'http': proxy[0] + ':' + proxy[1],
                                                        'https': proxy[0] + ':' + proxy[1]},
                         timeout=5)
        res = r.text.strip()
        custom_log("proxies are ok.", 'd')
        custom_log("waiting 3 second", 'd')
        time.sleep(3)
        return True, res
    except TimeoutError as e:
        res = "timeout"
        custom_log("check proxy availability: codal.ir loading problem" + str(e), 'd')
        custom_log("waiting 3 second", 'd')
        time.sleep(3)
        return False, res
    except Exception as e:
        res = "proxy exception"
        custom_log("check proxy availability: codal.ir loading problem" + str(e), 'd')
        custom_log("waiting 3 second", 'd')
        time.sleep(3)
        return False, res
