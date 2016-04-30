# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProxyModel(User):
    class Meta:
        proxy = True

    def get_display_name(self):
        if self.first_name:
            return self.first_name
        else:
            return self.username


class Tag(models.Model):
    title = models.CharField(max_length=256)

    def __unicode__(self):
        return self.title


class Message(models.Model):
    message = models.TextField()
    user = models.ForeignKey(UserProxyModel)
    time = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True)