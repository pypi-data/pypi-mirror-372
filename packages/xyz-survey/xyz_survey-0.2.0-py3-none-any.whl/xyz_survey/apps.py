# -*- coding:utf-8 -*- 
from __future__ import unicode_literals
from django.apps import AppConfig

class Config(AppConfig):
    name = 'xyz_survey'
    label = 'survey'
    verbose_name = '调查问卷'

    def ready(self):
        from . import receivers
