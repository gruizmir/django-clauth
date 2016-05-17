# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import ClAuthToken, ClUserData


@admin.register(ClAuthToken)
class ClAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'id_token', 'token_type')


# TODO: Ver si vale la pena poner rut y otros datos como readonly
@admin.register(ClUserData)
class ClUserDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'rut')
