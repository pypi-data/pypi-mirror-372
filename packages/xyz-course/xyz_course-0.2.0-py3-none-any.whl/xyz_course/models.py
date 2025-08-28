# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.functional import cached_property
from xyz_util import modelutils
from xyz_util.modelutils import CodeMixin

class Category(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "类别"

    name = models.CharField("名称", max_length=255, unique=True)
    code = models.CharField("拼音缩写", max_length=64, db_index=True, blank=True, default="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

    def __str__(self):
        return self.name


class Course(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "课程"

    name = models.CharField("名称", max_length=255, unique=True)
    code = models.CharField("拼音缩写", max_length=64, db_index=True, blank=True, default="")
    category = models.ForeignKey(Category, verbose_name=Category._meta.verbose_name, null=True, blank=True, on_delete=models.PROTECT)
    description = models.CharField("简介", max_length=256, blank=True, default="")
    outline = models.TextField("大纲", blank=True, default="")
    data = modelutils.JSONField("数据", blank=True, default={})
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)
    is_active = models.BooleanField("有效", blank=False, default=True)

    def __str__(self):
        return self.name

    def __iter__(self):
        for c in self.outline_treenode:
            yield c

    @cached_property
    def outline_treenode(self):
        from xyz_util.textutils import hierarchy
        return hierarchy(self.outline, ['第(\d+)章','\n+\s*(\d+)\.'])

    @cached_property
    def outline_list(self):
        rs = []
        for a in list(self):
            rs += a.to_array()
        return rs

    def save(self, **kwargs):
        if self.is_active is None:
            self.is_active = True
        super(Course, self).save(**kwargs)


class Chapter(CodeMixin, models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "章节"
        unique_together = ('course', 'name')
        order_with_respect_to = 'course'

    course = models.ForeignKey(Course, verbose_name=Course._meta.verbose_name, related_name="chapters",  on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=256)
    code = models.CharField("拼音缩写", max_length=64, db_index=True, blank=True, default="")
    order_num = models.PositiveIntegerField("序号", default=0, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

    def __str__(self):
        return self.name

class Pass(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "通过"
        unique_together = ('course', 'user')
        order_with_respect_to = 'course'

    course = models.ForeignKey(Course, verbose_name=Course._meta.verbose_name, related_name="passes",  on_delete=models.PROTECT)
    user = models.ForeignKey('auth.user', verbose_name='用户', related_name="passes",  on_delete=models.PROTECT)
    is_pass = models.BooleanField('已通过', blank=True, default=True)
    score = models.PositiveSmallIntegerField('分数', blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

