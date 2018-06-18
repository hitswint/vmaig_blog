from django.db import models


class ArticlePipegallery(models.Model):
    """Model for Articles."""
    title = models.CharField(max_length=40, verbose_name=u"标题")
    author = models.CharField(max_length=40, verbose_name=u"作者")

    def __unicode__(self):
        return self.title

    __str__ = __unicode__
