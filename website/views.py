from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from codal.models import Company, CompanyProfile


def index(request):
    context = {'page_title': 'ربات بورسی کدال با سلنیوم'}
    return render(request, 'index.html', context)


def report_view(request, report_tag):
    context = {'page_title': 'صفحه گزارشات'}
    if request.method == 'GET':
        if request.user.is_authenticated and request.user.is_superuser:
            if report_tag == '1':
                queryset = CompanyProfile.objects.filter(is_monthly_report_ready=True).order_by(
                    '-monthly_report_comparison_1_4')
                only_seasonal_ready = CompanyProfile.objects.filter(is_monthly_report_ready=False,
                                                                    is_seasonal_report_ready=True).order_by('-id')

                context['companies_profile'] = queryset
                context['companies_with_only_seasonal_ready'] = only_seasonal_ready
                return render(request, 'monthly-sort.html', context)
            elif report_tag == '2':
                queryset = CompanyProfile.objects.filter(is_monthly_report_ready=True).order_by(
                    '-monthly_report_comparison_2_5')
                only_seasonal_ready = CompanyProfile.objects.filter(is_monthly_report_ready=False,
                                                                    is_seasonal_report_ready=True).order_by('-id')
                context['companies_profile'] = queryset
                context['companies_with_only_seasonal_ready'] = only_seasonal_ready
                return render(request, 'monthly-sort.html', context)
            elif report_tag == '3':
                queryset = CompanyProfile.objects.filter(is_monthly_report_ready=True).order_by(
                    '-monthly_report_comparison_3_6')
                only_seasonal_ready = CompanyProfile.objects.filter(is_monthly_report_ready=False,
                                                                    is_seasonal_report_ready=True).order_by('-id')
                context['companies_profile'] = queryset
                context['companies_with_only_seasonal_ready'] = only_seasonal_ready
                return render(request, 'monthly-sort.html', context)
            elif report_tag == 'spring':
                companies_green = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_spring_color='green').order_by(
                    '-seasonal_report_spring_percentage')
                context['companies_green'] = companies_green
                companies_blue = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_spring_color='blue').order_by(
                    '-seasonal_report_spring_percentage')
                context['companies_blue'] = companies_blue

                companies_black = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_spring_color='black').order_by(
                    '-seasonal_report_spring_percentage')
                context['companies_black'] = companies_black

                companies_red = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                              seasonal_report_spring_color='red').order_by(
                    '-seasonal_report_spring_percentage')
                context['companies_red'] = companies_red

                companies_none = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_spring_color=None)
                context['companies_none'] = companies_none
                return render(request, 'seasonal-sort.html', context)
            elif report_tag == 'summer':
                companies_green = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_summer_color='green').order_by(
                    '-seasonal_report_summer_percentage')
                context['companies_green'] = companies_green
                companies_blue = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_summer_color='blue').order_by(
                    '-seasonal_report_summer_percentage')
                context['companies_blue'] = companies_blue

                companies_black = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_summer_color='black').order_by(
                    '-seasonal_report_summer_percentage')
                context['companies_black'] = companies_black

                companies_red = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                              seasonal_report_summer_color='red').order_by(
                    '-seasonal_report_summer_percentage')
                context['companies_red'] = companies_red

                companies_none = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_summer_color=None)
                context['companies_none'] = companies_none
                return render(request, 'seasonal-sort.html', context)
            elif report_tag == 'fall':
                companies_green = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_fall_color='green').order_by(
                    '-seasonal_report_fall_percentage')
                context['companies_green'] = companies_green
                companies_blue = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_fall_color='blue').order_by(
                    '-seasonal_report_fall_percentage')
                context['companies_blue'] = companies_blue

                companies_black = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_fall_color='black').order_by(
                    '-seasonal_report_fall_percentage')
                context['companies_black'] = companies_black

                companies_red = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                              seasonal_report_fall_color='red').order_by(
                    '-seasonal_report_fall_percentage')
                context['companies_red'] = companies_red

                companies_none = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_fall_color=None)
                context['companies_none'] = companies_none
                return render(request, 'seasonal-sort.html', context)
            elif report_tag == 'winter':
                companies_green = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_winter_color='green').order_by(
                    '-seasonal_report_winter_percentage')
                context['companies_green'] = companies_green
                companies_blue = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_winter_color='blue').order_by(
                    '-seasonal_report_winter_percentage')
                context['companies_blue'] = companies_blue

                companies_black = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                                seasonal_report_winter_color='black').order_by(
                    '-seasonal_report_winter_percentage')
                context['companies_black'] = companies_black

                companies_red = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                              seasonal_report_winter_color='red').order_by(
                    '-seasonal_report_winter_percentage')
                context['companies_red'] = companies_red

                companies_none = CompanyProfile.objects.filter(is_seasonal_report_ready=True,
                                                               seasonal_report_winter_color=None)
                context['companies_none'] = companies_none
                return render(request, 'seasonal-sort.html', context)
            else:
                queryset = CompanyProfile.objects.filter(is_monthly_report_ready=True).order_by('id')

                only_seasonal_ready = CompanyProfile.objects.filter(is_monthly_report_ready=False,
                                                                    is_seasonal_report_ready=True).order_by('-id')
                context['companies_profile'] = queryset
                context['companies_with_only_seasonal_ready'] = only_seasonal_ready
                return render(request, 'monthly-sort.html', context)
        else:
            return JsonResponse({"message": "you are not authorized to view the content"})
    else:
        return JsonResponse({"message": "you are not authorized to view the content"})
