# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import helper


class ViewsMixin(object):

    def retrieve(self, request, *args, **kwargs):
        helper.log_views(self.queryset.model._meta.label_lower, kwargs.get('pk'))
        return super(ViewsMixin, self).retrieve(request, *args, **kwargs)
