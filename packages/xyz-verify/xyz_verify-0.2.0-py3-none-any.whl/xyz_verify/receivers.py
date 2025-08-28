# -*- coding:utf-8 -*-
# author = 'denishuang'
from __future__ import unicode_literals
from django.dispatch import receiver
from .signals import to_create_verify, on_notify_verify_owner
from . import models, choices, serializers
from django.db.models.signals import post_save
import logging
from django.contrib.contenttypes.models import ContentType
from xyz_restful.signals import batch_action_post

log = logging.getLogger('django')


@receiver(to_create_verify)
def create_verify(sender, **kwargs):
    target = kwargs.pop('target')
    force = kwargs.pop('force', False)
    func = models.Verify.objects.update_or_create if force else models.Verify.objects.get_or_create
    verify, created = func(
        target_type=ContentType.objects.get_for_model(target),
        target_id=target.id,
        defaults=dict(
            status=choices.STATUS_PENDING,
            name=kwargs.get('name', str(target)),
            content=kwargs.get('content', {}),
            user=kwargs.get('user')
        )
    )
    return serializers.VerifySerializer(verify).data


# @receiver(post_save, sender=models.Verify)
# def notify(sender, **kwargs):
#     created = kwargs['created']
#     if created:
#         return
#     v = kwargs['instance']
#     print('sender:', type(v.target))
#     on_notify_verify_owner.send_robust(sender=type(v.target), instance=v)


@receiver(batch_action_post, sender=models.Verify)
def on_batch_passed(sender, **kwargs):
    if kwargs.get('field_name') != 'status':
        return
    qset = kwargs.get('queryset')
    for v in qset:
        try:
            on_notify_verify_owner.send(sender=type(v.target), instance=v)
        except:
            import traceback
            log.error('verify on_batch_passed error: %s', traceback.format_exc())
        # print(rs)
