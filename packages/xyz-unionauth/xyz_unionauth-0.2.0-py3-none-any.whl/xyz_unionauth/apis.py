# -*- coding:utf-8 -*-
from __future__ import division, unicode_literals
from django.http.response import HttpResponse

__author__ = 'denishuang'

from . import models, serializers, helper
from rest_framework import viewsets, decorators, status
from xyz_restful.decorators import register


@register()
class SourceViewSet(viewsets.ModelViewSet):
    queryset = models.Source.objects.all()
    serializer_class = serializers.SourceSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
    }
    search_fields = ('name', 'token')
    user_field_name = 'creator'

    def filter_queryset(self, queryset):
        if self.action == 'login':
            return queryset
        return super(SourceViewSet, self).filter_queryset(queryset)

    @decorators.action(['GET'], detail=True, permission_classes=[])
    def login(self, request, pk):
        source = self.get_object()
        d = helper.extract_profile(source, request)
        if not d:
            return HttpResponse('登录失败, 验证码无效，请联系系统管理员处理。', status=status.HTTP_403_FORBIDDEN)
        if source.procedure:
            func = helper.import_function(source.procedure)
            account = func(source, d)
            if account.user and account.user.is_authenticated:
                from django.contrib import auth
                auth.login(request, account.user)
        source.accounts.update_or_create(
            remote_id=d.get('number'),
            defaults=dict(profile=d)
        )
        return HttpResponse('登录成功')
        # return HttpResponseRedirect(source.landing_page)


@register()
class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    filterset_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'source': ['exact'],
    }
    search_fields = ('name',)
