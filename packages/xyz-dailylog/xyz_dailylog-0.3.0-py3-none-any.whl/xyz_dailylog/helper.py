# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType
from six import text_type

from . import models
from logging import getLogger
from time import sleep
log = getLogger('django')


def do_daily_stat(the_date):
    d = {}
    for l in models.DailyLog.objects.filter(the_date=the_date):
        for k, v in l.context.items():
            ps = k.split('.')
            app, model, mid, category, metric = ps
            am = (app, model)
            mt = "%s.%s" % (category, metric)
            r = d.setdefault(am, {}).setdefault(mid, {}).setdefault(mt, {'v': 0, 'u': 0})
            r['u'] += 1
            r['v'] += v
            r2 = d.setdefault(am, {}).setdefault(None, {}).setdefault(mt, {'v': 0, 'u': 0, 'us': set()})
            r2['us'].add(l.user.id)
            r2['u'] = len(r2['us'])
            r2['v'] += v
    for am, dam in d.items():
        ct = ContentType.objects.get_by_natural_key(am[0], am[1])
        for oid, doid in dam.items():
            for mt, dmt in doid.items():
                models.Stat.objects.update_or_create(
                    the_date=the_date,
                    owner_type=ct,
                    owner_id=oid,
                    metics=mt,
                    defaults=dict(
                        value=dmt['v'],
                        user_count=dmt['u']
                    )
                )
    return d


def save_record_by_rdb(r):
    try:
        models.Record.objects.update_or_create(
            the_date=r['the_date'],
            owner_type_id=r['owner_type_id'],
            owner_id=r['owner_id'],
            metics=r['metics'],
            user_id=r['user_id'],
            defaults=r
        )
    except Exception as e:
        import traceback
        log.error('save_record_by_rdb(%s) error: %s', r, traceback.format_exc())


def save_record_by_mongo(r):
    from .stores import Record
    rst = Record()
    cond = dict(
        the_date=r['the_date'],
        owner_type_id=r['owner_type_id'],
        owner_id=r['owner_id'],
        metics=r['metics'],
        user_id=r['user_id']
    )
    rst.upsert(cond, r)


def gen_dailylog_records(the_date, process=save_record_by_rdb):
    ocache = {}
    for l in models.DailyLog.objects.filter(the_date=the_date):
        user = l.user
        user_name = user.get_full_name()
        user_group = ''
        if hasattr(user, 'as_school_student'):
            user_group = ','.join(user.as_school_student.classes.values_list('name', flat=True))
        for k, v in l.context.items():
            ps = k.split('.')
            if len(ps) != 5:
                continue
            app, model, mid, category, metric = ps
            mt = "%s.%s" % (category, metric)
            odata = ocache.setdefault((mt, mid), {})
            if not odata:
                ct = ContentType.objects.get_by_natural_key(app, model)
                odata['owner_type_id'] = ct.id
                owner = ct.get_object_for_this_type(pk=mid)
                odata['owner_name'] = text_type(owner)
                odata['owner_group'] = ''
                if hasattr(owner, 'owner'):
                    odata['owner_group'] = text_type(owner.owner)
            record = dict(
                the_date=the_date,
                owner_id=mid,
                metics=mt,
                user_id=user.id,
                value=v,
                user_group=user_group,
                user_name=user_name,
                **odata
            )
            process(record)
            sleep(0.05)

def save_performance(d, user):
    ct = ContentType.objects.get(app_label=d['app'], model=d['model'])
    p, created = models.Performance.objects.update_or_create(
        user=user,
        owner_type=ct,
        owner_id=d['owner_id'],
        defaults=dict(
            detail=d['detail']
        ))
    return p


def get_performance(d, user):
    ct = ContentType.objects.get(app_label=d['app'], model=d['model'])
    p, created = models.Performance.objects.get_or_create(user=user, owner_type=ct, owner_id=d['owner_id'], defaults={})
    return p


def log_views(model, id):
    try:
        from .stores import ObjectLog
        ol = ObjectLog()
        ol.log(model, id)
    except:
        import traceback
        log.error('dailylog log_views error: %s', traceback.format_exc())

def save_user_daily(user_id, metics='online', model='auth.user', event_sender=None,**kwargs):
    from .stores import DailyLog
    st = DailyLog()
    print(f'metics:{metics}')
    r = st.log(user_id, model, metics=metics, **kwargs)
    from .signals import user_log
    user_log.send_robust(sender=event_sender, user_id=user_id, model=model, metics=metics)
    return r
