# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.contrib.auth.models import User
from xyz_util import modelutils


class Project(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "计划"

    name = models.CharField('名称', max_length=64)
    is_active = models.BooleanField('有效', default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "科目"

    project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name, related_name='subjects',
                                on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64)
    function = modelutils.JSONField('程序', blank=True, null=True)
    is_active = models.BooleanField('有效', blank=True, default=True)
    coefficient = models.PositiveIntegerField('系数', blank=True, default=1)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "子榜"

    project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name, related_name='categories',
                                on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64)
    is_active = models.BooleanField('有效', blank=True, default=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return '%s榜' % self.name


class Session(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "周期"

    project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name, related_name='sessions',
                                on_delete=models.PROTECT)
    name = models.CharField('名称', max_length=64, blank=True, default='第一期')
    number = models.PositiveIntegerField('序号', )
    is_active = models.BooleanField('有效', default=True)
    begin_time = models.DateTimeField("开始时间", blank=True)
    end_time = models.DateTimeField("结束时间", blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def save(self, **kwargs):
        if not self.name:
            self.name = '第%s期' % self.number
        from datetime import datetime, timedelta
        if not self.begin_time:
            self.begin_time = datetime.now()
        if not self.end_time:
            self.end_time = self.begin_time + timedelta(days=365)
        super(Session, self).save(**kwargs)

    def __str__(self):
        return self.name


class Point(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "积分"

    project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name, related_name='points',
                                on_delete=models.PROTECT)
    session = models.ForeignKey(Session, verbose_name=Session._meta.verbose_name, related_name='points',
                                on_delete=models.PROTECT)
    category = models.ForeignKey(Category, verbose_name=Category._meta.verbose_name, blank=True, null=True,
                                 related_name='points', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="points",
                             on_delete=models.PROTECT)
    value = models.PositiveIntegerField("数额", blank=True, default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def save(self, **kwargs):
        self.project = self.session.project
        super(Point, self).save(**kwargs)

    def __str__(self):
        return '%s积%s分' % (self.category or '', self.value)


class Item(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "明细"
        unique_together = ('point', 'user', 'owner_type', 'owner_id')

    point = models.ForeignKey(Point, verbose_name=Point._meta.verbose_name, related_name='items',
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="points_items",
                             on_delete=models.PROTECT)
    owner_type = models.ForeignKey('contenttypes.ContentType', verbose_name='归类', null=True, blank=True,
                                   on_delete=models.PROTECT)
    owner_id = models.PositiveIntegerField(verbose_name='属主编号', null=True, blank=True, db_index=True)
    owner = GenericForeignKey('owner_type', 'owner_id')
    owner_name = models.CharField('属主名称', max_length=256, blank=True, default='')
    value = models.PositiveIntegerField("数额", blank=True, default=0)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    def save(self, **kwargs):
        self.user = self.point.user
        super(Item, self).save(**kwargs)

    def __str__(self):
        return '积%s分自%s' % (self.value, self.owner_name)
