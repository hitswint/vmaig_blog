from django.utils.decorators import classonlymethod
from django.utils.version import get_version
from django.views.generic import View, TemplateView, ListView, DetailView
from django.shortcuts import render
from django.core.cache import caches
from django.db.models import Q
from django.conf import settings
from swint.models import ArticleSwint, CategorySwint, CommentSwint
from swint.forms import EmailArticleForm, CommentForm
from django.http import HttpResponse, JsonResponse
import os
import json
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from numpy import linspace, sin, shape
# import swint.fd_nopac as fd
# django自带的发送邮件的模块发送邮件失败。
from django.core.mail import send_mail
# Python对SMTP支持有smtplib和email两个模块，email负责构造邮件，smtplib负责发送邮件。
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

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

    template_name = 'swint/index.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM  # 分页--每页的数目

    # def get_context_data(self, **kwargs):
    #     # 轮播
    #     kwargs['carousel_page_list'] = Carousel.objects.all()
    #     return super(IndexView, self).get_context_data(**kwargs)

    def get_queryset(self):
        article_list = ArticleSwint.objects.filter(status=0)
        return article_list


# * Category_View
class Category_View(Base_Mixin, ListView):
    """view for category.html"""
    template_name = 'swint/category.html'
    context_object_name = 'article_list'
    paginate_by = settings.PAGE_NUM

    def get_queryset(self):
        category = self.kwargs.get('category', '')
        try:
            article_list = \
                           CategorySwint.objects.get(name=category).articleswint_set.all()
        except CategorySwint.DoesNotExist:
            logger.error(u'[Category_View]此分类不存在:[%s]' % category)
            raise Http404

        return article_list


# * User_View
class User_View(Base_Mixin, TemplateView):
    template_name = 'swint/user.html'

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            logger.error(u'[User_View]用户未登陆')
            return render(request, 'swint/login.html')

        slug = self.kwargs.get('slug')

        if slug == 'changetx':
            self.template_name = 'swint/user_changetx.html'
        elif slug == 'changepassword':
            self.template_name = 'swint/user_changepassword.html'
        elif slug == 'changeinfo':
            self.template_name = 'swint/user_changeinfo.html'
        elif slug == 'message':
            self.template_name = 'swint/user_message.html'
        elif slug == 'notification':
            self.template_name = 'swint/user_notification.html'

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
    queryset = ArticleSwint.objects.filter(Q(status=0) | Q(status=1))
    template_name = 'swint/article.html'
    context_object_name = 'article'
    # 从url中获得id值为slug_url_kwarg，并在queryset中使用slug_field过滤。
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
            except ArticleSwint.DoesNotExist:
                logger.error(u'[ArticleView]访问不存在的文章:[%s]' % article_id)
                raise Http404
            else:
                article.view_times += 1
                article.save()
                visited_ips.append(ip)

            # 更新缓存
            cache.set(article_id, visited_ips, 15 * 60)

        return super(Article_View, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Form was submitted
        # List of active comments for this post
        article = self.get_object()
        comments = article.comments.filter(active=True)
        new_comment = None

        # A comment was posted
        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            # Create Comment object but don't save to database yet.
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.article = article
            # Save the comment to the database
            new_comment.save()
            # else:
            # comment_form = CommentForm()
            # return render(request,
            #               'blog/post/detail.html',
            #               {'post': post,
            #                'comments': comments,
            #                'new_comment': new_comment,
            #                'comment_form': comment_form})

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # 评论
        # en_title = self.kwargs.get('slug', '')
        # kwargs['comment_list'] = \
        #     self.queryset.get(en_title=en_title).comment_set.all()
        article = self.get_object()
        kwargs['comments'] = article.comments.all()
        if self.request.method == 'POST':
            # Form was submitted
            kwargs['comment_form'] = CommentForm(data=self.request.POST)
        else:
            kwargs['comment_form'] = CommentForm()
        return super(Article_View, self).get_context_data(**kwargs)


# * Article_Share_View
class Article_Share_View(Base_Mixin, DetailView):
    queryset = ArticleSwint.objects.filter(Q(status=0) | Q(status=1))
    template_name = 'swint/article_share.html'
    context_object_name = 'article'
    # 从url中获得id值为slug_url_kwarg，并在queryset中使用slug_field过滤。
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def post(self, request, *args, **kwargs):
        # Form was submitted
        form = EmailArticleForm(request.POST)
        article = self.get_object()
        kwargs['sent'] = False

        def mail_content(from_addr, to_addr):
            msg = MIMEText(article.title, 'plain', 'utf-8')
            msg['From'] = from_addr  # Header('<%s>' % from_addr, 'utf-8')
            msg['To'] = to_addr  # Header('<%s>' % to_addr, 'utf-8')
            msg['Subject'] = Header('Hello World', 'utf-8').encode()
            return msg

        if form.is_valid():
            cd = form.cleaned_data
            # Form fields passed validation
            article_url = article.get_absolute_url()

            from_addr = cd['email']
            password = 'hIT850119'  # input('Password: ')
            to_addr = cd['to']
            smtp_server = 'smtp.163.com'
            msg = mail_content(from_addr, to_addr)
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            # 使用django自带的邮件模块发送邮件，失败。
            # subject = '{} ({}) recommends you reading "{}"'.format(
            #     cd['name'], cd['email'], article.title)
            # message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(
            #     article.title, article_url, cd['name'], cd['comments'])
            # send_mail(subject, message, 'wguiqiang@hotmail.com', [cd['to']])
            kwargs['cd'] = cd
            kwargs['sent'] = True

        self.object = self.get_object()
        context = self.get_context_data(object=self.object, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        if self.request.method == 'POST':
            # Form was submitted
            kwargs['emailform'] = EmailArticleForm(self.request.POST)
        else:
            kwargs['emailform'] = EmailArticleForm()
        return super(Article_Share_View, self).get_context_data(**kwargs)
