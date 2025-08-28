# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from xyz_restful.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models


class SurveySerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Survey
        exclude = ()
        read_only_fields = ('user', 'questions_count', 'target_user_count', 'actual_user_count')


class SurveyListSerializer(SurveySerializer):
    class Meta(SurveySerializer.Meta):
        exclude = ('content_object', 'content')


class AnswerSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        exclude = ()
        read_only_fields = ('user', )

class AnswerListSerializer(AnswerSerializer):
    class Meta(AnswerSerializer.Meta):
        exclude = ('detail',)
