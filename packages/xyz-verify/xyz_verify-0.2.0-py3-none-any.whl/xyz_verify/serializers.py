# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class VerifySerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    user_name = serializers.CharField(label='用户', source='user.get_full_name', read_only=True)
    operator_name = serializers.CharField(label='审核员', source='operator.get_full_name', read_only=True)

    class Meta:
        model = models.Verify
        fields = (
        'user', 'user_name', 'target_type', 'target_id', 'name', 'status', 'create_time', 'category', 'content',
        'reply', 'operator', 'operator_name')
