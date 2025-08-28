# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save
import logging

log = logging.getLogger('django')


# @receiver(post_save, sender=models.Crawler)
# def gen_search_crawler_sources(sender, **kwargs):
#     crawler = kwargs['instance']
#     created = kwargs['created']
#     if not created or crawler.mode != choices.MODE_SEARCH:
#         return
#     from . import tasks
#     tasks.gen_search_crawler_sources.delay(crawler.id)

