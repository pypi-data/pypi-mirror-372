# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from xyz_util import modelutils


class Survey(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "问卷"
        ordering = ("-is_active", "title")

    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="surveys", on_delete=models.PROTECT)
    title = models.CharField("标题", max_length=255)
    content = models.TextField("内容", blank=True, null=True,
                               help_text="编辑指南:\n首行为标题.\n题目用阿拉伯数字加点号开头.\n选项用英文字母加点号开头.")
    content_object = modelutils.JSONField("内容对象", blank=True, null=True, help_text="")
    is_active = models.BooleanField('有效', default=False)
    questions_count = models.PositiveSmallIntegerField("题数", blank=True, default=0)
    target_user_tags = models.CharField('目标人群标签', max_length=255, null=True, blank=True,
                                        help_text="符合标签的人才能填写问卷,留空则所有人均可填写但不会发个人通知.<p>"
                                                  "例子:<p>老师:张三,李四,赵五<p>学生:*<p>学生.年级:大一,大二<p>学生.入学届别:2019届<p>学生.班级:2018级数字媒体201801班,2018级数字媒体201804班")
    target_user_count = models.PositiveIntegerField('目标参与人数', default=0, blank=True)
    actual_user_count = models.PositiveIntegerField('实际参与人数', default=0, blank=True)
    begin_time = models.DateTimeField("开始时间", help_text="开始时间一到问卷会被自动上线")
    end_time = models.DateTimeField("结束时间", help_text="结束时间一到问卷会被自动下线")
    invite_text = models.CharField("邀请致辞", max_length=256, blank=True, null=True)
    thanks_text = models.CharField("感谢致辞", max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_target_user_ids(self):
        from xyz_auth.helper import find_user_ids_by_tag
        tags = self.target_user_tags
        if tags:
            return set(find_user_ids_by_tag(tags))
        return set()

    def get_actual_user_ids(self):
        return set(self.answers.values_list("user_id", flat=True))

    def get_not_answer_user_ids(self):
        return self.get_target_user_ids().difference(self.get_actual_user_ids())

    def save(self, **kwargs):
        # if self.target_user_count == None:
        data = self.content_object
        if data:
            self.questions_count = data.get("questionCount", 0)
        self.target_user_count = len(self.get_target_user_ids())
        super(Survey, self).save(**kwargs)



class Answer(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "答卷"
        unique_together = ("survey", "user")

    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="survey_answers", blank=True, on_delete=models.PROTECT)
    survey = models.ForeignKey(Survey, related_name="answers", on_delete=models.PROTECT)
    detail = modelutils.JSONField("详情", help_text="")
    create_time = models.DateTimeField("创建时间", auto_now_add=True, null=True, blank=True)

    def user_name(self):
        return self.user and self.user.get_full_name()

    user_name.short_description = '用户姓名'

    def show_content(self):
        return "\n".join(["%s : %s" % (d.get("name"), d.get("value")) for d in self.detail])

    show_content.short_description = '答卷展示'
