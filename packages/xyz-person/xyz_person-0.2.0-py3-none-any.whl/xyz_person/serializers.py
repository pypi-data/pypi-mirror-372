# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class PersonSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    user_account = serializers.CharField(source='user.username', label='帐号', read_only=True)
    class Meta:
        model = models.Person
        fields = '__all__'
