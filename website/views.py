from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from codal.models import Company


def index(request):
    context = {'page_title': 'ربات بورسی کدال با سلنیوم'}
    return render(request, 'index.html', context)


def report_view_1(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            queryset = Company.objects.filter(is_monthly_report_ready=True).order_by(
                '-date_finished')

            only_seasonal_ready = Company.objects.filter(is_monthly_report_ready=False, is_seasonal_report_ready=True).order_by('-id')
            return render(request, 'home.html', {'title': "report",
                                                 'companies': queryset,
                                                 'extra': only_seasonal_ready,
                                                 })
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")


def report_view_2(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            queryset = Company.objects.filter(is_monthly_report_ready=True).order_by(
                '-monthly_report_comparison_1_4')
            only_seasonal_ready = Company.objects.filter(is_monthly_report_ready=False, is_seasonal_report_ready=True).order_by('-id')
            return render(request, 'home.html', {'title': "report",
                                                 'companies': queryset,
                                                 'extra': only_seasonal_ready,
                                                 })
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")


def report_view_3(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            queryset = Company.objects.filter(is_monthly_report_ready=True).order_by(
                '-monthly_report_comparison_2_5')
            only_seasonal_ready = Company.objects.filter(is_monthly_report_ready=False, is_seasonal_report_ready=True).order_by('-id')
            return render(request, 'home.html', {'title': "report",
                                                 'companies': queryset,
                                                 'extra': only_seasonal_ready,
                                                 })
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")


def report_view_4(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            queryset = Company.objects.filter(is_monthly_report_ready=True).order_by(
                '-monthly_report_comparison_3_6')
            only_seasonal_ready = Company.objects.filter(is_monthly_report_ready=False, is_seasonal_report_ready=True).order_by('-id')
            return render(request, 'home.html', {'title': "report",
                                                 'companies': queryset,
                                                 'extra': only_seasonal_ready,
                                                 })
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")


def report_spring(request):
    context = {'title': "report spring"}
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            companies_green = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_spring_color='green').order_by('-seasonal_report_spring_percentage')
            context['companies_green'] = companies_green
            companies_blue = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_spring_color='blue').order_by('-seasonal_report_spring_percentage')
            context['companies_blue'] = companies_blue

            companies_black = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_spring_color='black').order_by('-seasonal_report_spring_percentage')
            context['companies_black'] = companies_black

            companies_red = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_spring_color='red').order_by('-seasonal_report_spring_percentage')
            context['companies_red'] = companies_red

            companies_none = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_spring_color=None)
            context['companies_none'] = companies_none
            return render(request, 'seasonal-sort.html', context)
        else:
            return JsonResponse({'message': 'you are not authorized to view the content'})
    else:
        return JsonResponse({'message': 'you are not authorized to view the content'})


def report_summer(request):
    context = {'title': "report summer"}
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            companies_green = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_summer_color='green').order_by('-seasonal_report_summer_percentage')
            context['companies_green'] = companies_green
            companies_blue = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_summer_color='blue').order_by('-seasonal_report_summer_percentage')
            context['companies_blue'] = companies_blue

            companies_black = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_summer_color='black').order_by('-seasonal_report_summer_percentage')
            context['companies_black'] = companies_black

            companies_red = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_summer_color='red').order_by('-seasonal_report_summer_percentage')
            context['companies_red'] = companies_red

            companies_none = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_summer_color=None)
            context['companies_none'] = companies_none
            return render(request, 'seasonal-sort.html', context)
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")


def report_fall(request):
    context = {'title': "report fall"}
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            companies_green = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_fall_color='green').order_by(
                '-seasonal_report_fall_percentage')
            context['companies_green'] = companies_green
            companies_blue = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_fall_color='blue').order_by(
                '-seasonal_report_fall_percentage')
            context['companies_blue'] = companies_blue

            companies_black = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_fall_color='black').order_by(
                '-seasonal_report_fall_percentage')
            context['companies_black'] = companies_black

            companies_red = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_fall_color='red').order_by(
                '-seasonal_report_fall_percentage')
            context['companies_red'] = companies_red

            companies_none = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_fall_color=None)
            context['companies_none'] = companies_none
            return render(request, 'seasonal-sort.html', context)
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")


def report_winter(request):
    context = {'title': "report winter"}
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            companies_green = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_winter_color='green').order_by('-seasonal_report_winter_percentage')
            context['companies_green'] = companies_green
            companies_blue = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_winter_color='blue').order_by('-seasonal_report_winter_percentage')
            context['companies_blue'] = companies_blue

            companies_black = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_winter_color='black').order_by('-seasonal_report_winter_percentage')
            context['companies_black'] = companies_black

            companies_red = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_winter_color='red').order_by('-seasonal_report_winter_percentage')
            context['companies_red'] = companies_red

            companies_none = Company.objects.filter(is_seasonal_report_ready=True, seasonal_report_winter_color=None)
            context['companies_none'] = companies_none
            return render(request, 'seasonal-sort.html', context)
        else:
            return HttpResponse("you are not authorized to view the content")
    else:
        return HttpResponse("you are not authorized to view the content")