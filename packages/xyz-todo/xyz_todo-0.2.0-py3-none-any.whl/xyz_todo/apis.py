# -*- coding:utf-8 -*-
from __future__ import division
from xyz_restful.mixins import UserApiMixin
from rest_framework.viewsets import GenericViewSet

from . import models, serializers
from rest_framework import mixins, decorators
from xyz_restful.decorators import register


@register()
class TodoViewSet(UserApiMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = models.Todo.objects.all()
    serializer_class = serializers.TodoSerializer
    filterset_fields = {
        'user': ['exact'],
        'is_done': ['exact'],
        'expiration': ['gt', 'lt']
    }

    def get_queryset(self):
        qset = super(TodoViewSet, self).get_queryset()
        if self.action == 'current':
            from datetime import datetime
            user = self.request.user
            if user.is_authenticated:
                qset = qset.filter(user=user, is_done=False, expiration__gt=datetime.now())
        return qset

    @decorators.action(methods=['GET'], detail=False)
    def current(self, request):
        return self.list(request)
