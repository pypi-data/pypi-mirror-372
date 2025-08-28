# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.dispatch import Signal

to_create_todos = Signal()
to_cancel_todos = Signal()
todo_done = Signal()