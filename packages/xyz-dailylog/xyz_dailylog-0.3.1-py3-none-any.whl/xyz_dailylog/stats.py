# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import models
from django.db.models import Count, Sum, Max
from xyz_util import statutils

def stats_stat(qset=None, measures=None, period=None, time_field=None):
    qset = qset if qset is not None else models.Stat.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'the_date')
    funcs = {
        'daily': lambda: dstat.stat(period, count_field='id', distinct=True),
    }
    return dict([(m, funcs[m]()) for m in measures])


def stats_record(qset=None, measures=None, period=None, time_field=None):
    qset = qset if qset is not None else models.Record.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'the_date')
    funcs = {
        'all': lambda: qset.count(),
        'daily': lambda: dstat.group_by(period, measures=[Count('user', distinct=True), Sum('value')]),
        # 'exercise_done': lambda : dstat.group_by(measures=[Sum('value'), Count('user', distinct=True)]),
        'user_group': lambda: statutils.group_by(
            dstat.get_period_query_set(period),
            'user_group',
            measures=[Count('user', distinct=True), Sum('value')],
            sort="-"),
        'owner': lambda: statutils.group_by(
            dstat.get_period_query_set(period),
            "owner_group,owner_name",
            measures=[Count('user', distinct=True), Sum('value')],
            sort="-"),
        'owner_group': lambda: statutils.group_by(
            dstat.get_period_query_set(period),
            "owner_group",
            measures=[Count('user', distinct=True), Sum('value')],
            sort="-")
    }
    return dict([(m, funcs[m]()) for m in measures])
