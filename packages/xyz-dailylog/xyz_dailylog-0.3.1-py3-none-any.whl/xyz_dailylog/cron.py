# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, print_function
from . import models, helper


def do_dailylog_stat(the_date=None):
    from datetime import date
    the_date = the_date or date.today()
    print('do_dailylog_stat', the_date)
    helper.do_daily_stat(the_date)

def gen_dailylog_records(the_date=None):
    from datetime import date
    the_date = the_date or date.today()
    print('gen_dailylog_records', the_date)
    helper.gen_dailylog_records(the_date)
