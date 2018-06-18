from django.utils.version import get_version
from django.views.generic import View, TemplateView, ListView, DetailView
from django.shortcuts import render
from django.core.cache import caches
from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from pipe_gallery_simu.models import ArticlePipegallery
import os
import json
import logging
import matplotlib.animation as animation
from numpy import linspace, sin, shape, argmax, argmin
import pipe_gallery_simu.simu as simu
from django.utils.decorators import classonlymethod
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# Create your views here.

# 缓存
try:
    cache = caches['memcache']
except ImportError as e:
    cache = caches['default']

logger = logging.getLogger(__name__)


# * Base_Mixin
class Base_Mixin(object):
    """Basic mix class."""

    def get_context_data(self, *args, **kwargs):
        context = super(Base_Mixin, self).get_context_data(**kwargs)
        try:
            # 网站标题等内容
            context['website_title'] = settings.WEBSITE_TITLE
            context['website_welcome'] = settings.WEBSITE_WELCOME
            context['django_version'] = get_version()
            user = self.request.user
            if user.is_authenticated():
                context[
                    'notification_count'] = user.to_user_notification_set.filter(
                        is_read=0).count()
        except Exception:
            logger.error(u'[BaseMixin]加载基本信息出错')

        return context


# * PipegalleryView
class PipegalleryView(Base_Mixin, ListView):
    """view for pipegallerysimu.html"""
    model = ArticlePipegallery
    template_name = 'pipe_gallery_simu/pipegallerysimu.html'

    @classonlymethod
    def simu_submit(self, request):

        # Acquire data from request.GET.
        Num_pipegallery = int(request.GET.get('Num_pipegallery'))
        Length_pipegallery = float(request.GET.get('Length_pipegallery'))
        Num = int(request.GET.get('Num'))
        T_gallery = float(request.GET.get('T_gallery'))
        T_gas_in = float(request.GET.get('T_gas_in'))
        T_air_in = float(request.GET.get('T_air_in'))
        V_gas = float(request.GET.get('V_gas'))
        V_air = float(request.GET.get('V_air'))
        radiation_included_p = request.GET.get(
            'radiation_included_p') == 'true'
        result_list = simu.main(
            Num_pipegallery=Num_pipegallery,
            Length_pipegallery=Length_pipegallery,
            Num=Num,
            T_gallery=T_gallery,
            T_gas_in=T_gas_in,
            T_air_in=T_air_in,
            V_gas=V_gas,
            V_air=V_air,
            radiation_included_p=radiation_included_p)

        return JsonResponse(result_list, safe=False)
