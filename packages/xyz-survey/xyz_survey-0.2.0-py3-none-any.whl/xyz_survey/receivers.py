# -*- coding:utf-8 -*-
from django.dispatch import receiver
from . import models, helper
from django.db.models.signals import post_save, post_delete, pre_save
from xyz_common.signals import to_save_version

import logging

log = logging.getLogger('django')

@receiver(post_save, sender=models.Survey)
def survey_update_todo(sender, **kwargs):
    survey = kwargs.pop('instance')
    if survey.is_active == True:
        created = kwargs['created']
        if not created:
            helper.revoke_survey_todos(survey)
        helper.create_survey_todos(survey)
    else:
        helper.revoke_survey_todos(survey)

@receiver(post_delete, sender=models.Survey)
def survey_remove_todo(sender, **kwargs):
    survey = kwargs.pop('instance')
    helper.revoke_survey_todos(survey)

@receiver(post_save, sender=models.Answer)
def survey_done_todo(sender, **kwargs):
    answer = kwargs.pop('instance')
    try:
        from xyz_todo.helper import todo_done
        todo_done(answer.survey, answer.user)
    except:
       import traceback
       log.error('survey_done_todo error: %s', traceback.format_exc())

    created = kwargs['created']
    if created:
        survey = answer.survey
        c = int(survey.answers.count())
        models.Survey.objects.filter(id=survey.id).update(actual_user_count=c)


@receiver(pre_save, sender=models.Survey)
def save_survey_version(sender, **kwargs):
    to_save_version.send_robust(sender, instance=kwargs['instance'])

