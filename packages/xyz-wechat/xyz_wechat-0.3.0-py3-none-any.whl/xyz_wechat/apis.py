# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import urls
from xyz_restful.helper import register_urlpatterns
from .apps import Config

register_urlpatterns(Config.label, urls)
