# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from six import text_type
from xyz_util import modelutils

class Comment(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "评论"
        ordering = ('-create_time', )

    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="comments")
    content_type = models.ForeignKey(ContentType, verbose_name=ContentType._meta.verbose_name, null=True, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(null=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, db_index=True, null=True, blank=True)
    content = models.TextField("内容")
    context = models.TextField("上下文", blank=True, default='')
    anchor = models.CharField("锚点", max_length=256, blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    is_active = models.BooleanField("有效", default=True)
    reply_count = models.PositiveIntegerField('回贴数', blank=True, default=0, editable=False)

    def save(self, **kwargs):
        if not self.object_name:
            self.object_name = text_type(self.content_object)
        return super(Comment, self).save(**kwargs)

    def __unicode__(self):
        return "%s 评论 %s" % (self.user.get_full_name(), self.object_name)

    @property
    def replies(self):
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(Comment)
        qs = Comment.objects.filter(content_type=ct, object_id=self.id)
        return qs


class Favorite(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "收藏"
        ordering = ('-create_time',)
        unique_together = ('user', 'content_type', 'object_id')

    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="comment_favorites")
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(null=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, db_index=True, null=True, blank=True)
    notes = modelutils.JSONField("笔记", blank=True, default={})
    notes_count = models.PositiveSmallIntegerField('笔记数', blank=True, default=1)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    is_active = models.BooleanField("有效", default=True)

    def save(self, **kwargs):
        if not self.object_name:
            self.object_name = text_type(self.content_object)
        if not self.notes:
            self.notes = {}
        self.notes_count = len([n for n in self.notes.values() if n['is_active']])
        self.is_active = self.notes_count > 0
        return super(Favorite, self).save(**kwargs)

    def __unicode__(self):
        return "%s 收藏 %s" % (self.user.get_full_name(), self.object_name)


class Rating(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "评分"
        ordering = ('-create_time',)

    user = models.ForeignKey("auth.User", on_delete=models.PROTECT, null=True, related_name="comment_ratings")
    content_type = models.ForeignKey(ContentType, verbose_name=ContentType._meta.verbose_name, null=True, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(null=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, db_index=True, null=True, blank=True)
    stars = models.PositiveSmallIntegerField('评分', default=0, blank=True)
    content = models.TextField("内容", blank=True, default='')
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

    def save(self, **kwargs):
        if not self.object_name:
            self.object_name = text_type(self.content_object)
        return super(Rating, self).save(**kwargs)

    def __unicode__(self):
        return "%s 评分 %s" % (self.user.get_full_name(), self.object_name)

class RatingSumary(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "评分汇总"
        unique_together = ('content_type', 'object_id')

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(null=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_name = models.CharField("名称", max_length=256, db_index=True, null=True, blank=True)
    score = models.DecimalField('评分', max_digits=3, decimal_places=1, default=0, blank=True)
    user_count = models.PositiveSmallIntegerField('参与人数', default=0, blank=True)
    detail = modelutils.JSONField('详情', default={}, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

    def save(self, **kwargs):
        if not self.object_name:
            self.object_name = text_type(self.content_object)
        return super(RatingSumary, self).save(**kwargs)
