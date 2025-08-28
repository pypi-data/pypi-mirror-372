# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from . import models
from xyz_util import statutils

def stats_verify(qset=None, measures=None, period=None):
    qset = qset if qset is not None else models.Verify.objects.all()
    qset = statutils.using_stats_db(qset)
    dstat = statutils.DateStat(qset, 'create_time')
    funcs = {
        'today': lambda: dstat.stat("今天", only_first=True),
        'yesterday': lambda: dstat.stat("昨天", only_first=True),
        'all': lambda: qset.count(),
        'daily': lambda: dstat.stat(period),
        'status': lambda: dstat.group_by(period, ['status']),
    }
    return dict([(m, funcs[m]()) for m in measures])

