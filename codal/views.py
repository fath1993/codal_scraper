from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache
from codal.tasks import run_thread, codal_scraper
from codal_scraper.celery import app


@never_cache
def robot(request, ck):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            i = app.control.inspect()
            number_of_active_task = 0
            celery_active_task_ids = []
            for worker in i.active():
                print(worker)
                all_active_task_list = i.active()[worker]
                number_of_active_task = len(all_active_task_list)
                for celery_task in all_active_task_list:
                    celery_task_id = celery_task['id']
                    celery_active_task_ids.append(celery_task_id)
                    celery_task_name = celery_task['name']
                    print('celery task id: ' + celery_task_id)
                    print('celery task name: ' + celery_task_name)
                    print('***')
            print('------------------------------')
            print('number of active task: ' + str(number_of_active_task))
            if ck == "start":
                if number_of_active_task == 0:
                    codal_scraper.delay()
                    return JsonResponse({'message': 'robot has started'})
                else:
                    return JsonResponse({'message': 'robot had worked before it has started'})
            elif ck == "stop":
                if number_of_active_task == 0:
                    return JsonResponse({'message': 'robot has not worked'})
                else:
                    # app.control.revoke(celery_active_task_ids, terminate=True)
                    app.control.purge()
                    # app.control.terminate(celery_active_task_ids)
                    app.control.broadcast('pool_restart')
                    return JsonResponse({'message': 'robot has stopped'})
            else:
                pass
        return HttpResponse("you are not authorized")
    return HttpResponse("you are not authorized")
