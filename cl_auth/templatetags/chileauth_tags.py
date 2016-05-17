# -*- coding: utf-8 -*-
import urllib
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def clave_unica_url(session_token):
    cu_settings = settings.CHILE_AUTH_SETTINGS.get('clave_unica', {})
    params = {
        'client_id': cu_settings['client_id'],
        'response_type': 'code',
        'scope': ' '.join(cu_settings.get('scope', ['openid', 'sandbox'])),
        'redirect_uri': cu_settings.get('callback',
                                        reverse('callback_claveunica')),
        'state': session_token
    }
    url = 'https://www.claveunica.gob.cl/openid/authorize?' + urllib(params)
    return url


@register.simple_tag
def clave_unica_auth(session_token):
    url = clave_unica_url(session_token)
    link = '<a href=\"%s\">Ingresar a través de ClaveÚnica</a>' % url
    return link
