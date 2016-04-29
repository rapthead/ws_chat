# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Tag(models.Model):
    title = models.CharField(max_length=256)


class Message(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User)
    time = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True)
