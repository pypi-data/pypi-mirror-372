# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.dispatch import Signal

user_log = Signal(use_caching=True)