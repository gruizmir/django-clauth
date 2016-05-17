# -*- coding: utf-8 -*-


def auth_token(request):
    if 'cl_auth_state_token' in request.session:
        return {'cl_auth_token': request.session['chileauth_state_token']}
    return {}