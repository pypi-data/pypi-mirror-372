# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class DailyLogSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.DailyLog
        exclude = ()
        read_only_fields = ('user', 'create_time')

class StatSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner", label='对象')
    class Meta:
        model = models.Stat
        exclude = ()
        read_only_fields = ('user', 'create_time')



class RecordSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Record
        exclude = ()
        read_only_fields = ('user', 'create_time')


class PerformanceSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Performance
        exclude = ()
        read_only_fields = ('user', 'create_time')

