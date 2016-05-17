# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns("chileauth.callbacks",
    url(r"^callbacks/claveunica/$", 'claveunica', name="callback_claveunica"),

)
