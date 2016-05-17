# -*- coding: utf-8 -*-
import uuid


class ClAuthMiddleware(object):
    u"""
    Verifica si la sesión del usuario tiene creado un token para usar en la
    autenticación con medios externos. Si no existe, la crea y la agrega a la
    sesión.
    """
    def process_request(self, request):
        if not 'cl_auth_state_token' in request.session:
            request.session['cl_auth_state_token'] = \
                                            str(uuid.uuid4()).replace('-', '')