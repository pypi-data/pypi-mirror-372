# -*- coding:utf-8 -*-
from __future__ import division

from xyz_restful.mixins import UserApiMixin
from .apps import Config
__author__ = 'denishuang'
from . import models, serializers
from rest_framework import viewsets
from xyz_restful.decorators import register


@register()
class PersonViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Person.objects.all()
    serializer_class = serializers.PersonSerializer
    filterset_fields = ('gender',)
    search_fields = ('name',)

