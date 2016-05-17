# -*- coding: utf-8 -*-
u"""
Django ORM models for authenticated users.

Uso:
Si se ocupa un modelo de usuario distinto al que ofrece Django por defecto, se
debe declarar en la variable AUTH_USER_MODEL en settings.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

try:
    USER_MODEL = settings.AUTH_USER_MODEL
except:
    USER_MODEL = User


class ClAuthToken(models.Model):
    user = models.ForeignKey(USER_MODEL, related_name='chile_auth_token')
    id_token = models.CharField(max_length=120)
    access_token = models.CharField(max_length=120)
    token_type = models.CharField(max_length=20)
    access_code = models.CharField(max_length=120)

    class Meta:
        app_label = 'chileauth'

    def __unicode__(self):
        return unicode(self.user)


class ClUserData(models.Model):
    user = models.ForeignKey(USER_MODEL, related_name='chile_auth_data')
    rut = models.CharField('RUT', max_length=12, null=True, blank=True)
    name = models.CharField('RUT', max_length=12, null=True, blank=True)

    class Meta:
        app_label = 'chileauth'

    def __unicode__(self):
        return unicode(self.user)