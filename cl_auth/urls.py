# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .callbacks import ClaveUnicaCallback


urlpatterns = patterns("cl_auth.callbacks",
    url(r"^callbacks/claveunica/$", ClaveUnicaCallback.as_view(),
                                    name="callback_claveunica"),

)
