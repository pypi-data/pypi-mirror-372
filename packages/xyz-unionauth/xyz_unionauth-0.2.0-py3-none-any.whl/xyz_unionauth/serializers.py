# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models

class SourceSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Source
        exclude = ()


class AccountSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', label=models.Source._meta.verbose_name, read_only=True)
    class Meta:
        model = models.Account
        exclude = ()
        read_only_fields = ('create_time',)
