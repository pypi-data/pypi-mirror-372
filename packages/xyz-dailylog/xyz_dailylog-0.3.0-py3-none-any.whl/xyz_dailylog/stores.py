# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from six import string_types
from xyz_util.mongoutils import Store

from xyz_util.datautils import access
from xyz_util.dateutils import format_the_date


class ObjectLog(Store):
    name = 'object_log'
    timeout = 1000

    def log(self, model, id, metics={'views': 1}):
        vs = dict([(k, int(v)) for k, v in metics.items()])
        self.inc({'model': model, 'id': int(id)}, vs)

    def find(self, model, ids, metics='views'):
        return self.collection.find({'model': model, 'id': {'$in': ids}}, {'_id': '$id', 'count': '$' + metics})


class UserLog(Store):
    name = 'user_log'
    timeout = 1000

    def log(self, id, metics='online_time', **kwargs):
        if isinstance(metics, str):
            delta = kwargs.get('delta', 1)
            if isinstance(delta, string_types):
                delta = int(delta)
            metics = {metics: delta}
        self.inc({'id': int(id)}, metics)
        # self.inc({'id': int(id)}, {metics: int(delta)})
        a = self.collection.find_one({'id': int(id)}, dict([(k, 1) for k in metics]))
        if not a:
            return None
        a.pop('_id')
        return a
        # return access(a, metics) if a else None

    def max(self, id, metics='online_time', value=1):
        a = self.collection.find_one({'id': int(id)}, {metics: 1})
        old = access(a, metics) if a else None
        if old is None or old < value:
            self.upsert({'id': int(id)}, {metics: int(value)})
            return value
        return old

    def set(self, id, metics='online_time', value=1):
        self.upsert({'id': int(id)}, {metics: int(value)})
        return {metics: int(value)}

    def get(self, id, metics='online_time'):
        d = self.collection.find_one({'id': id}, {metics: 1})
        return access(d, metics) if d else None

    def list(self, id, metic_list=[]):
        if isinstance(metic_list, (tuple, list)):
            metic_list = dict([(a, 1) for a in metic_list])
        return self.collection.find_one({'id': id}, metic_list)


class DailyLog(Store):
    name = 'daily_log'
    timeout = 1000

    def log(self, user, model, metics='done', the_date=None, **kwargs):
        d = format_the_date(the_date)
        rk = dict(user=user, model=model, date=d.isoformat())
        if isinstance(metics, str):
            delta = kwargs.get('delta', 1)
            if isinstance(delta, string_types):
                delta = int(delta)
            metics = {metics: delta}
        self.inc(rk, metics)
        # a = self.collection.find_one(rk, {metics: 1})
        # r = access(a, metics)


class UserDailyLog(Store):
    name = 'user_daily_log'


class ObjectDailyLog(Store):
    name = 'object_daily_log'


class Record(Store):
    name = 'dailylog_record'

