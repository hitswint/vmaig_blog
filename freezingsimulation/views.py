from django.utils.version import get_version
from django.views.generic import View, TemplateView, ListView, DetailView
from django.shortcuts import render
from django.core.cache import caches
from django.db.models import Q
from django.conf import settings
from freezingsimulation.models import ArticleFreezingsimu, CategoryFreezingsimu
from django.http import HttpResponse, JsonResponse
import os
import json
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from numpy import linspace, sin, shape, argmax, argmin
import freezingsimulation.fd_nopac as fd
from django.utils.decorators import classonlymethod
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


# * Index_View
class Index_View(Base_Mixin, ListView):
    """view for index.html"""

    template_name = 'freezingsimulation/index.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM  # 分页--每页的数目

    def get_queryset(self):
        article_list = ArticleFreezingsimu.objects.filter(status=0)
        return article_list


# * Freezingsimu
class Freezingsimu_View(Base_Mixin, ListView):
    """view for freezingsimu.html"""

    template_name = 'freezingsimulation/freezingsimu.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM  # 分页--每页的数目

    def get_queryset(self):
        article_list = ArticleFreezingsimu.objects.filter(status=0)
        return article_list

# ** Freezingsimu-DoingSimulation.

    @classonlymethod
    def simu(self, request):

        # Acquire data from request.GET.
        food_product = request.GET.get('food_product')
        temperature = request.GET.get('temperature')
        heattr = request.GET.get('heattr')
        shelfthickness = request.GET.get('shelfthickness')
        food_product = float(food_product)
        temperature = float(temperature)
        heattr = float(heattr)
        shelfthickness = float(shelfthickness)

        file_dir = 'static/img/simu/'
        plot_file_base_name = 'simu_{}_{}_{}_{}'.format(
            food_product, temperature, heattr, shelfthickness)

        # Doing simulation actually.
        Tc, Ts_top, Ts_bottom, qq_top, qq_bottom, time, T_all, H_all = fd.freezing_simu(
            Ta=temperature, Tp=food_product, ha=heattr,
            dp=shelfthickness).simu()
        T_all = T_all[0:T_all.shape[0]:100]
        H_all = H_all[0:H_all.shape[0]:100]

        # Plot on temperature change of thermal center.
        fig1, ax1 = plt.subplots(figsize=(5, 5), dpi=98)
        ax1.set_title(u'食品温度变化', fontproperties='KaiTi')
        ax1.set_xlabel(u'冷冻时间(小时)', fontproperties='KaiTi')
        ax1.set_ylabel(u'食品温度(\u2103)', fontproperties='KaiTi')
        ax1.plot(time[0:len(time):100], Tc[0:len(Tc):100], 'yo',
                 time[0:len(time):100], Ts_bottom[0:len(Ts_bottom):100], 'ms',
                 time[0:len(time):100], Ts_top[0:len(Ts_top):100], 'cs')
        fig1.savefig(
            os.path.join(file_dir, ''.join([plot_file_base_name, '_1.png'])))

        # Plot on heat load change.
        fig2 = plt.figure(figsize=(5, 5), dpi=98)
        p2 = fig2.add_subplot(111)
        plt.title(u'食品负荷变化', fontproperties='KaiTi')
        plt.xlabel(u'冷冻时间(小时)', fontproperties='KaiTi')
        plt.ylabel(u'食品负荷(W)', fontproperties='KaiTi')
        p2.plot(time[0:len(time):100], qq_top[0:len(qq_top):100], 'mo',
                time[0:len(time):100], qq_bottom[0:len(qq_bottom):100], 'cs')
        fig2.savefig(
            os.path.join(file_dir, ''.join([plot_file_base_name, '_2.png'])))

        # Animation on temperature change of food product.
        fig3, ax3 = plt.subplots(figsize=(5, 5))
        ax3.set_xlim(-1, 24)
        ax3.set_ylim(-30, 30)
        ax3.set_title(u'食品离散点温度', fontproperties='KaiTi')
        ax3.set_xlabel(u'离散点', fontproperties='KaiTi')
        ax3.set_ylabel(u'温度(\u2103)', fontproperties='KaiTi')
        line3, = ax3.plot(
            range(T_all[1, ].shape[0]), T_all[1, ], 'r--o', linewidth=2)
        n3 = argmax(T_all[1, ])
        line3_center, = ax3.plot(
            (range(T_all[1, ].shape[0])[n3], range(T_all[1, ].shape[0])[n3]),
            (T_all[1, ][n3] - 5, T_all[1, ][n3] + 5),
            'g-o',
            linewidth=2)

        def update3(data):
            line3.set_ydata(data)
            line3_center.set_xdata((range(data.shape[0])[argmax(data)],
                                    range(data.shape[0])[argmax(data)]))
            line3_center.set_ydata((data[argmax(data)] - 5,
                                    data[argmax(data)] + 5))
            return line3, line3_center

        ani3 = animation.FuncAnimation(fig3, update3, T_all, interval=1 * 800)
        ani3.save(
            os.path.join(file_dir, ''.join([plot_file_base_name, '_1.gif'])),
            dpi=80,
            writer='imagemagick')

        # Animation on enthalpy change of food product.
        fig4, ax4 = plt.subplots(figsize=(5, 5))
        ax4.set_xlim(-1, 24)
        ax4.set_ylim(0, 4e8)
        ax4.set_title(u'食品离散点焓值', fontproperties='KaiTi')
        ax4.set_xlabel(u'离散点', fontproperties='KaiTi')
        ax4.set_ylabel(u'焓值(\u2103)', fontproperties='KaiTi')
        line4, = ax4.plot(
            range(H_all[1, ].shape[0]), H_all[1, ], 'g-.s', linewidth=2)
        n4 = argmax(H_all[1, ])
        line4_center, = ax4.plot(
            (range(H_all[1, ].shape[0])[n4], range(H_all[1, ].shape[0])[n4]),
            (H_all[1, ][n4] - 0.3e8, H_all[1, ][n4] + 0.3e8),
            'r-s',
            linewidth=2)

        def update4(data):
            line4.set_ydata(data)
            line4_center.set_xdata((range(data.shape[0])[argmax(data)],
                                    range(data.shape[0])[argmax(data)]))
            line4_center.set_ydata((data[argmax(data)] - 0.3e8,
                                    data[argmax(data)] + 0.3e8))
            return line4, line4_center

        ani4 = animation.FuncAnimation(fig4, update4, H_all, interval=1 * 800)
        ani4.save(
            os.path.join(file_dir, ''.join([plot_file_base_name, '_2.gif'])),
            dpi=80,
            writer='imagemagick')

        plt.close('all')

        # Filter figs and append numbers.
        freezing_time = '{} 小时'.format(round(time[-1], 2))
        freezing_rate = '{} cm/h'.format(
            round(0.005 * 23 * 100 / (time[argmin(abs(Tc - (-0.78 - 5)))] -
                                      time[argmin(abs(Ts_top))]), 2))
        result_list = list(
            filter(lambda x: x.startswith(plot_file_base_name),
                   os.listdir(file_dir)))
        result_list.append(freezing_time)
        result_list.append(freezing_rate)
        return JsonResponse(result_list, safe=False)


# * Category_View
class Category_View(Base_Mixin, ListView):
    """view for category.html"""
    template_name = 'freezingsimulation/category.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_queryset(self):
        category = self.kwargs.get('category', '')
        try:
            article_list = \
                           CategoryFreezingsimu.objects.get(name=category).articlefreezingsimulation_set.all()
        except CategoryFreezingsimu.DoesNotExist:
            logger.error(u'[Category_View]此分类不存在:[%s]' % category)
            raise Http404

        return article_list


# * User_View
class User_View(Base_Mixin, TemplateView):
    template_name = 'freezingsimulation/user.html'

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            logger.error(u'[User_View]用户未登陆')
            return render(request, 'freezingsimulation/login.html')

        slug = self.kwargs.get('slug')

        if slug == 'changetx':
            self.template_name = 'freezingsimulation/user_changetx.html'
        elif slug == 'changepassword':
            self.template_name = 'freezingsimulation/user_changepassword.html'
        elif slug == 'changeinfo':
            self.template_name = 'freezingsimulation/user_changeinfo.html'
        elif slug == 'message':
            self.template_name = 'freezingsimulation/user_message.html'
        elif slug == 'notification':
            self.template_name = 'freezingsimulation/user_notification.html'

        return super(User_View, self).get(request, *args, **kwargs)

        logger.error(u'[User_View]不存在此接口')
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(User_View, self).get_context_data(**kwargs)

        slug = self.kwargs.get('slug')

        if slug == 'notification':
            context['notifications'] = \
                                       self.request.user.to_user_notification_set.order_by(
                                           '-create_time'
                                       ).all()

        return context


# * Article_View
class Article_View(Base_Mixin, DetailView):
    queryset = ArticleFreezingsimu.objects.filter(Q(status=0) | Q(status=1))
    template_name = 'freezingsimulation/article.html'
    context_object_name = 'article'
    # 从url中获得id值为slug_url_kwarg，并在objects中使用slug_field过滤。
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        # 获取访问网站的用户的ip地址。
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
            self.cur_user_ip = ip

        article_id = self.kwargs.get('id')
        # 获取15*60s时间内访问过这篇文章的所有ip
        visited_ips = cache.get(article_id, [])

        # 如果ip不存在就把文章的浏览次数+1。
        if ip not in visited_ips:
            try:
                article = self.queryset.get(id=article_id)
            except ArticleFreezingsimu.DoesNotExist:
                logger.error(u'[ArticleView]访问不存在的文章:[%s]' % article_id)
                raise Http404
            else:
                article.view_times += 1
                article.save()
                visited_ips.append(ip)

            # 更新缓存
            cache.set(article_id, visited_ips, 15 * 60)

        return super(Article_View, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # 评论
        # en_title = self.kwargs.get('slug', '')
        # kwargs['comment_list'] = \
        #     self.queryset.get(en_title=en_title).comment_set.all()
        return super(Article_View, self).get_context_data(**kwargs)
