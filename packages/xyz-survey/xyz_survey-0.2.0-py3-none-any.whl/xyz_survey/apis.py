# -*- coding:utf-8 -*-
from __future__ import division
from xyz_restful.mixins import UserApiMixin, BatchActionMixin
from . import models, serializers
from rest_framework import viewsets, decorators, response
from xyz_restful.decorators import register


@register()
class SurveyViewSet(UserApiMixin, BatchActionMixin, viewsets.ModelViewSet):
    queryset = models.Survey.objects.all()
    serializer_class = serializers.SurveySerializer
    search_fields = ('title',)
    filterset_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'content': ['contains'],
        'begin_time': ['range']
    }
    ordering_fields = ('is_active', 'title', 'create_time', 'questions_count')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.SurveyListSerializer
        return super(SurveyViewSet, self).get_serializer_class()

    @decorators.action(['POST'], detail=False)
    def batch_active(self, request):
        return self.do_batch_action('is_active', True)

    @decorators.action(['GET'], detail=True)
    def result(self, request, pk):
        from . import helper
        survey = helper.stat_survey_answers(self.get_object())
        serializer = self.get_serializer_class()(survey)
        return response.Response(serializer.data)

@register()
class AnswerViewSet(UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer
    filterset_fields = ('survey', 'user')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AnswerListSerializer
        return super(AnswerViewSet, self).get_serializer_class()


