# -*- coding:utf-8 -*-
from __future__ import division
from xyz_restful.mixins import UserApiMixin, BatchActionMixin
from xyz_util.statutils import do_rest_stat_action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from . import models, serializers, stats, choices
from rest_framework import decorators
from xyz_restful.decorators import register


@register()
class VerifyViewSet(UserApiMixin, BatchActionMixin, ModelViewSet):
    queryset = models.Verify.objects.all()
    serializer_class = serializers.VerifySerializer
    filterset_fields = {
        'category': ['exact'],
        'create_time': ['range'],
        'target_type': ['exact'],
        'target_id': ['exact'],
        'status': ['exact']
    }
    search_fields = ['name']
    ordering_fields = ('name', 'create_time', 'update_time')

    @decorators.action(['get'], detail=False)
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_verify)

    def perform_update(self, serializer):
        serializer.save(operator=self.request.user)

    def get_permissions(self):
        if self.action in ['current']:
            return [IsAuthenticated()]
        return super(VerifyViewSet, self).get_permissions()

    def get_queryset(self):
        qset = super(VerifyViewSet, self).get_queryset()
        if self.action == 'current':
            qset = qset.filter(user=self.request.user, status=choices.STATUS_PENDING)
        return qset

    @decorators.action(methods=['GET'], detail=False)
    def current(self, request):
        return self.list(request)

    @decorators.action(['POST'], detail=False)
    def batch_pass(self, request):
        return self.do_batch_action('status', choices.STATUS_PASS, extra_params=dict(operator=request.user))
