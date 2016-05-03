# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProxyModel(User):
    class Meta:
        proxy = True

    def display_name(self):
        if self.first_name:
            return self.first_name
        else:
            return self.username


class Tag(models.Model):
    title = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title


class Message(models.Model):
    message = models.TextField(verbose_name=u"Сообщение")
    user = models.ForeignKey(UserProxyModel, verbose_name=u"Пользователь")
    time = models.DateTimeField(default=timezone.now, verbose_name=u"Время")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=u"Теги")
