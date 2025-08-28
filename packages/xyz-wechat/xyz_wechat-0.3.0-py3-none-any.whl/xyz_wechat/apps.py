# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig
from django.conf import settings

__author__ = 'denishuang'


class Config(AppConfig):
    name = "xyz_wechat"
    label = 'wechat'
    verbose_name = "微信"

    def ready(self):
        super(Config, self).ready()
        from . import receivers


MP = settings.WECHAT.get("MP", {})
