# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from xyz_util import modelutils
from django.utils.crypto import get_random_string


class Source(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "来源"

    name = models.CharField('名称', max_length=64)
    is_active = models.BooleanField('有效', default=True)
    token = models.CharField('令牌', max_length=64, blank=True, null=True)
    landing_page = models.CharField('落地页', max_length=255, blank=True, default='/')
    procedure = models.CharField('处理函数', max_length=128, blank=True, null=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.token:
            self.token = get_random_string(32, 'abcdefghijklmnopqrstuvwxyz0123456789')
        super(Source, self).save(**kwargs)


class Account(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "帐号"
        unique_together = ('source', 'remote_id')

    source = models.ForeignKey(Source, verbose_name=Source._meta.verbose_name, related_name="accounts",
                               on_delete=models.PROTECT)
    remote_id = models.CharField('源ID', max_length=64)
    name = models.CharField('姓名', max_length=64)
    profile = modelutils.JSONField('档案')
    is_active = models.BooleanField('有效', default=True)
    user = models.OneToOneField(User, verbose_name=User._meta.verbose_name, null=True,
                                related_name="as_unionauth_account", on_delete=models.PROTECT)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("创建时间", auto_now=True)

    def __str__(self):
        return '%s@%s' % (self.name, self.source)
