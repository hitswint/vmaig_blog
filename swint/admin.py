# -*- coding: utf-8 -*-
from django.contrib import admin
from swint.models import ArticleSwint, CategorySwint, CommentSwint

# Carousel, Nav, Column, News


class CategoryAdminSwint(admin.ModelAdmin):
    search_fields = ('name', )
    list_filter = ('status', 'create_time')
    list_display = ('name', 'parent', 'status')
    fields = ('name', 'parent', 'status')


class ArticleAdminSwint(admin.ModelAdmin):
    search_fields = ('title', 'summary')
    list_filter = ('status', 'category', 'create_time', 'modify_time')
    list_display = ('title', 'category', 'status', 'create_time',
                    'modify_time')
    fieldsets = ((u'基本信息', {
        'fields': ('title', 'category', 'tags', 'status')
    }), (u'内容', {
        'fields': ('content', )
    }), (u'摘要', {
        'fields': ('summary', )
    }),
                 # (u'时间', {
                 #     'fields': ('create_time', )
                 # })
                 )


class CommentAdminSwint(admin.ModelAdmin):
    list_display = ('name', 'email', 'article', 'create_time', 'active')
    list_filter = ('active', 'create_time', 'modify_time')
    search_fields = ('name', 'email', 'content')


# class NewsAdmin(admin.ModelAdmin):
#     search_fields = ('title', 'summary')
#     list_filter = ('news_from', 'create_time')
#     list_display = ('title', 'news_from', 'url', 'create_time')
#     fields = ('title', 'news_from', 'url', 'summary', 'pub_time')

# class NavAdmin(admin.ModelAdmin):
#     search_fields = ('name',)
#     list_display = ('name', 'url', 'status', 'create_time')
#     list_filter = ('status', 'create_time')
#     fields = ('name', 'url', 'status')

# class ColumnAdmin(admin.ModelAdmin):
#     search_fields = ('name',)
#     list_display = ('name', 'status', 'create_time')
#     list_filter = ('status', 'create_time')
#     fields = ('name', 'status', 'article', 'summary')
#     filter_horizontal = ('article',)

# class CarouselAdmin(admin.ModelAdmin):
#     search_fields = ('title',)
#     list_display = ('title', 'article', 'img', 'create_time')
#     list_filter = ('create_time',)
#     fields = ('title', 'article', 'img', 'summary')

admin.site.register(CategorySwint, CategoryAdminSwint)
admin.site.register(ArticleSwint, ArticleAdminSwint)
admin.site.register(CommentSwint, CommentAdminSwint)
# admin.site.register(News, NewsAdmin)
# admin.site.register(Nav, NavAdmin)
# admin.site.register(Column, ColumnAdmin)
# admin.site.register(Carousel, CarouselAdmin)
