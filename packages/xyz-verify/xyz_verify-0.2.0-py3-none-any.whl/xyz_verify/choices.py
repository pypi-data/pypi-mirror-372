# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

STATUS_PENDING = 0
STATUS_PASS = 1
STATUS_REJECT = 2

CHOICES_STATUS = (
    (STATUS_PENDING, '待决'),
    (STATUS_PASS, '通过'),
    (STATUS_REJECT, '否决'),
)