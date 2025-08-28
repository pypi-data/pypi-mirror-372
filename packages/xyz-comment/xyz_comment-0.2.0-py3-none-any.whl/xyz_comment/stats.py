# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import models
from xyz_util import statutils
from django.db.models import Sum

def stats_favorite(qset=None, measures=None, period=None, time_field=None):
    qset = qset if qset is not None else models.Fault.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, time_field or 'create_time')
    funcs = {
        'today': lambda: dstat.stat("今天", count_field="user_id", distinct=True, only_first=True),
        'count': lambda: dstat.get_period_query_set(period).count(),
        'all': lambda: qset.values("user_id").distinct().count(),
        'allCount': lambda: qset.count(),
        'notesCount': lambda: qset.aggregate(nc=Sum('notes_count'))['nc']
    }
    return dict([(m, funcs[m]()) for m in measures])

