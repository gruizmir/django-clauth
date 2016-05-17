# -*- coding: utf-8 -*-
import json
import requests
from django.conf import settings
from django.http import HttpResponseMethodNotAllowed, HttpResponseBadRequest,\
                        HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.views.generic import View
from .models import USER_MODEL, ClAuthToken, ClUserData

try:
    PROFILE_MODEL = settings.PROFILE_MODEL
except:
    PROFILE_MODEL = None


# TODO: Agregar verificación de restricciones de acceso de rut.
class ClaveUnicaCallback(View):
    # TODO: Verificar que exista el campo en settings
    redirect_url = settings.LOGIN_REDIRECT_URL or '/'

    def dispatch(self, request, *args, **kwargs):
        return super(ClaveUnicaCallback, self).dispatch(request=request,
                                                        *args, **kwargs)

    def get(self, request):
        if self.request.method == 'GET':
            request_state = request.GET.get('state', None)
            request_code = request.GET.get('code', None)
            session_state = request.session.pop('state', None)
            if not session_state or not request_state:
                return HttpResponseBadRequest()
            elif session_state != request_state:
                return HttpResponseForbidden()

            cu_settings = settings.CHILE_AUTH_SETTINGS.get('clave_unica', {})
            url = cu_settings.get('endpoint',
                                  'https://www.claveunica.gob.cl/openid/token/')
            payload = {
                'client_id': cu_settings['client_id'],
                'client_secret': cu_settings['client_secret'],
                'redirect_uri': cu_settings.get('callback',
                                                reverse('callback_claveunica')),
                'grant_type': 'authorization_code',
                'code': request_code,
                'state': request_state
            }
            # TODO: Poner límite de tiempo de respuesta
            response = requests.post(url, params=payload)

            # TODO: Verificar códigos de respuesta y errores que retorna
            if response.status_code == 200:
                json_response = json.loads(response.text)
            else:
                # TODO: Cambiar el error por uno que corresponda a datos malos
                return HttpResponseForbidden()

            # Loguear al usuario si existe, registrarlo y loguearlo si no.
            id_token = json_response['id_token']
            user_token, created = ClAuthToken.objects\
                                            .get_or_create(id_token=id_token)
            if created:
                # TODO: pedir rut para crear el usuario
                # Si el RUT ya existe, se debe asociar esta cuenta con ese RUT.
                user_info_url = cu_settings.get('info_url',
                            'https://www.claveunica.gob.cl/openid/userinfo')
                access_token = json_response['access_token']
                headers = {'Authorization': 'Bearer ' + access_token}
                info_response = requests.post(user_info_url,
                                         params={},
                                         headers=headers)
                rut = info_response.get('RUT', None)
                if rut:
                    rut = rut + info_response.get('sub', None)
                    # TODO: Nombre del campo de rut debería estar en settings
                    if PROFILE_MODEL:
                        profile = PROFILE_MODEL.objects.filter(rut=rut).first()
                        if profile:
                            # TODO: Nombre del campo FK de usuario debería ir en
                            # settings
                            user_token.user = profile.user
                            user_token.save()
                        # TODO: Crear el perfil al usuario
                    else:
                        user = USER_MODEL.objects.filter(username=rut).first()
                        if not user:
                            # TODO: Campo username desde settings
                            user = USER_MODEL.objects.create(username=rut,
                                                             password=id_token)
                        user_token.user = user
                        user_token.save()

                    # Se crea un registro de datos de usuario
                    user_data, data_created = ClUserData.objects\
                                                      .get_or_create(user=user)
                    if data_created:
                        user_data.rut = rut
                        user_data.name = info_response['nombre']
                        user_data.save()

            else:
                user = user_token.user
                login(request, user)
                user_token.access_token = json_response['access_token']
                user_token.token_type = json_response['token_type']
                user_token.save()
            return HttpResponseRedirect(self.redirect_url)
        else:
            return HttpResponseMethodNotAllowed(['GET'])
