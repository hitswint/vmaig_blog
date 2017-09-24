from django.db import models

# Create your models here.

STATUS = {
    0: u'正常',
    1: u'草稿',
    2: u'删除',
}


class CategoryFreezingsimu(models.Model):
    """Documentation for Category"""
    name = models.CharField(
        default=u'未分类', unique=True, max_length=40, verbose_name=u'类目')
    parent = models.ForeignKey(
        'self', default=None, blank=True, null=True, verbose_name=u'上级')
    status = models.IntegerField(
        default=0, choices=STATUS.items(), verbose_name=u'状态')
    create_time = models.DateTimeField(verbose_name=u'创建时间', auto_now_add=True)

    class Meta():
        verbose_name_plural = verbose_name = u'类目'
        ordering = ['-create_time', ]

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse(
            'freezingsimulation-category-detail-view', args=(self.id, ))

    def __unicode__(self):
        if self.parent:
            return '%s-->%s' % (self.parent, self.name)
        else:
            return '%s' % (self.name)

    __str__ = __unicode__


class ArticleFreezingsimu(models.Model):
    """Model for Articles."""
    # 引用外键Category，Category定义需在Article前面。
    category = models.ForeignKey(
        'CategoryFreezingsimu',
        on_delete=models.SET_DEFAULT,
        to_field='name',
        # null=True,
        default=u'未分类',
        verbose_name=u'类别')
    title = models.CharField(max_length=40, verbose_name=u"标题")
    tags = models.CharField(
        max_length=200,
        verbose_name=u"标签",
        help_text=u"用逗号分开",
        blank=True,
        null=True)
    image = models.CharField(
        max_length=200, default='/static/img/article/default.jpg')
    author = models.CharField(max_length=40, verbose_name=u"作者")
    summary = models.TextField(verbose_name=u"摘要")
    content = models.TextField(verbose_name=u"内容")
    status = models.IntegerField(
        default=0, choices=STATUS.items(), verbose_name=u'状态')
    view_times = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True)
    modify_time = models.DateTimeField(verbose_name=u"修改时间", auto_now=True)

    def get_tags(self, ):
        # 删除字符串中的空格并用逗号分割。
        tags_without_space = ''.join([x for x in self.tags if x != " "])
        tags_list = tags_without_space.split(',')
        while '' in tags_list:
            tags_list.remove('')
        return tags_list

    class Meta:
        verbose_name_plural = verbose_name = u'文章'
        ordering = ['-modify_time', '-create_time']

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse(
            'freezingsimulation-article-detail-view', args=(self.id, ))

    def __unicode__(self):
        return self.title

    __str__ = __unicode__
