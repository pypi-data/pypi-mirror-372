# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig

class Config(AppConfig):
    name = "xyz_todo"
    label = "todo"
    verbose_name = "待办"

    def ready(self):
        super(Config, self).ready()
        from . import receivers
