import os
import threading

from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from codal.tasks import codal_scraper, company_profile_updater, CodalScraperThread, CompanyProfileUpdaterThread
from custom_logs.models import custom_log


@never_cache
def robot(request, ck):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            print('number_of_active_thread: ' + str(threading.active_count()))
            print('main_thread: ' + str(threading.main_thread()))
            print('current_thread: ' + str(threading.current_thread()))
            print('current_thread id: ' + str(threading.get_ident()))
            print('current_thread native id: ' + str(threading.get_native_id()))
            print('list of all active thread: ' + str(threading.enumerate()))
            for thr in threading.enumerate():
                print(thr.name)
            custom_log('-------------- Thread supervisor starts----------------')
            is_robot_run = False
            custom_log(str(threading.enumerate()))
            for thr in threading.enumerate():
                custom_log(thr.name)
                if thr.name == 'codal_scraper':
                    is_robot_run = True
                    break
            if is_robot_run:
                custom_log('codal scraper is active')
            else:
                custom_log('codal scraper is not active')
            custom_log('-------------- Thread supervisor ends ----------------')
            if ck == "start":
                if not is_robot_run:
                    try:
                        os.rename('codal\\tasks_stopped.py', 'codal\\tasks.py')
                    except Exception as e:
                        print(str(e))
                    CodalScraperThread(name='codal_scraper').start()
                    return JsonResponse({'message': 'the codal scraper has been started'})
                else:
                    return JsonResponse({'message': 'the codal scraper is working'})
            elif ck == "stop":
                if not is_robot_run:
                    return JsonResponse({'message': 'the codal scraper is not working'})
                else:
                    for thr in threading.enumerate():
                        if thr.name == 'codal_scraper':
                            thr.raise_exception()
                            thr.join()
                    return JsonResponse({'message': 'the codal scraper has been stopped'})
            else:
                pass
        return HttpResponse("you are not authorized")
    return HttpResponse("you are not authorized")
