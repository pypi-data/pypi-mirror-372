# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from six import text_type

from . import models, choices

def target_records(target, **kwargs):
    qset = models.Verify.objects.filter(**kwargs)
    if isinstance(target, text_type):
        ct = ContentType.objects.get_by_natural_key(*target.split('.'))
        return qset.filter(target_type=ct)
    ct = ContentType.objects.get_for_model(target)
    return qset.filter(target_id=target.id, target_type=ct)

def batch_pass(qset, status=choices.STATUS_PASS):
    aids = list(qset.values_list('id', flat=True))
    qset.update(status=status)
    from xyz_restful.signals import batch_action_post
    batch_action_post.send(models.Verify, queryset=models.Verify.objects.filter(id__in=aids), field_name='status')