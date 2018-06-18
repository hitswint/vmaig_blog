from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap, Sitemap
from django.core.urlresolvers import reverse

from django.contrib import admin

from blog.models import Article, News, Category, Column


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['index-view', 'news-view']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'article-is-top':
    GenericSitemap(
        {
            'queryset': Article.objects.filter(status=0, is_top=True).all(),
            'date_field': 'pub_time'
        },
        priority=1.0,
        changefreq='daily'),
    'article-is-not-top':
    GenericSitemap(
        {
            'queryset': Article.objects.filter(status=0).all(),
            'date_field': 'pub_time'
        },
        priority=0.8,
        changefreq='daily'),
    'news':
    GenericSitemap(
        {
            'queryset': News.objects.all(),
            'data_field': 'pub_time'
        },
        priority=0.6,
        changefreq='daily'),
    'category':
    GenericSitemap(
        {
            'queryset': Category.objects.all()
        }, priority=0.9, changefreq='daily'),
    'column':
    GenericSitemap(
        {
            'queryset': Column.objects.all()
        }, priority=0.9, changefreq='daily'),
    'static':
    StaticViewSitemap
}

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('blog.urls')),
    url(r'', include('swint.urls')),
    url(r'', include('pipe_gallery_simu.urls')),
    url(r'', include('freezingsimulation.urls')),
    url(r'', include('vmaig_comments.urls')),
    url(r'', include('vmaig_auth.urls')),
    url(r'^sitemap\.xml$',
        sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap')
]

# 在Debug = False的非调试模式下，静态文件不会自动加载，而是交给apache/nginx来处理。
# 设置在非调试模式下同样加载静态文件。
# from django.conf import settings
# from django.views.static import serve
# if settings.DEBUG is False:
#     urlpatterns += [
#         url(r'^static/(?P<path>.*)$', serve, {
#             'document_root': settings.STATIC_ROOT,
#         }),
#     ]
