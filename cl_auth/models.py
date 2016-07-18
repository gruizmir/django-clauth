# -*- coding: utf-8 -*-
u"""
Django ORM models for authenticated users.

Uso:
Si se ocupa un modelo de usuario distinto al que ofrece Django por defecto, se
debe declarar en la variable AUTH_USER_MODEL en settings.
"""
from django.apps import apps
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

try:
    USER_MODEL = get_user_model()
except:
    USER_MODEL = User

try:
    PROFILE_MODEL = apps.get_model(settings.PROFILE_MODEL)
except:
    PROFILE_MODEL = None

class ClAuthToken(models.Model):
    user = models.ForeignKey(USER_MODEL, related_name='chile_auth_token')
    id_token = models.CharField(max_length=120)
    access_token = models.CharField(max_length=120)
    token_type = models.CharField(max_length=20)
    access_code = models.CharField(max_length=120)

    class Meta:
        app_label = 'cl_auth'

    def __unicode__(self):
        return unicode(self.user)


class ClUserData(models.Model):
    user = models.ForeignKey(USER_MODEL, related_name='chile_auth_data',
                            null=True)
    rut = models.CharField('RUT', max_length=12, null=True, blank=True)
    name = models.CharField('Names', max_length=50, null=True, blank=True)
    lastname_1 = models.CharField('Lastname_1', max_length=50, 
                                    null=True, blank=True)
    lastname_2 = models.CharField('Lastname_2', max_length=50, 
                                    null=True, blank=True)

    class Meta:
        app_label = 'cl_auth'

    def __unicode__(self):
        return unicode(self.user)
