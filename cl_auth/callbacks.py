# -*- coding: utf-8 -*-
import json
import requests
import urllib
from django.conf import settings
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest,\
                        HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.views.generic import View
from .models import USER_MODEL, ClAuthToken, ClUserData, PROFILE_MODEL


# TODO: Agregar verificación de restricciones de acceso de rut.
class ClaveUnicaCallback(View):
    # TODO: Verificar que exista el campo en settings
    redirect_url = settings.LOGIN_REDIRECT_URL or '/'

    def dispatch(self, request, *args, **kwargs):
        return super(ClaveUnicaCallback, self).dispatch(request=request,
                                                        *args, **kwargs)

    def get(self, request):
        request_state = request.GET.get('state', None)
        request_code = request.GET.get('code', None)
        session_state = request.session.pop('cl_auth_state_token', None)
        if not session_state or not request_state:
            # TODO: Solicitar template para el error o crear propio
            return HttpResponseBadRequest()
        elif session_state != request_state:
            # TODO: Solicitar template para el error o crear propio
            return HttpResponseForbidden()

        cu_settings = settings.CHILE_AUTH_SETTINGS.get('clave_unica', {})
        url = cu_settings.get('endpoint',
                              'https://www.claveunica.gob.cl/openid/token/')
        # TODO: Cambiar sitio por uno asociado
        site = Site.objects.first()
        redirect_uri = 'https://' + site.domain +\
                cu_settings.get('callback', reverse('callback_claveunica'))
        redirect_uri = urllib.quote_plus(redirect_uri)
        payload = {
            # TODO: Enviar warning si los campos no existen (para local)
            'client_id': cu_settings.get('client_id', None),
            'client_secret': cu_settings.get('client_secret', None),
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
            'code': request_code,
            'state': request_state
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; MotoG3'
            ' Build/MPI24.65-25) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/51.0.2704.81 Mobile Safari/537.36'}

        response = requests.post("http://httpbin.org/post", 
                            data=payload, headers=headers)
        # TODO: Poner límite de tiempo de respuesta
        response = requests.post(url, data=payload, headers=headers)

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
        if created or not user_token.user:
            # TODO: pedir rut para crear el usuario
            # Si el RUT ya existe, se debe asociar esta cuenta con ese RUT.
            user_info_url = cu_settings.get('info_url',
                        'https://www.claveunica.gob.cl/openid/userinfo')
            access_token = json_response['access_token']
            headers['Authorization'] = 'Bearer ' + access_token
            info_response = requests.post(user_info_url,
                                            data={},
                                            headers=headers)
            if info_response.status_code == 200:
                if settings.DEBUG:
                    print info_response.text
                response_data = json.loads(info_response.text)
                rut = response_data.get('RUT', None)
                if rut:
                    rut = rut
                    user, profile = self.get_user_profile(response_data,
                                                        id_token)
                    user_token.user = profile.user
                    user_token.save()
                    # Se crea un registro de datos de usuario
                    user_data, data_created = ClUserData.objects\
                                                    .get_or_create(user=user)   
                    if data_created:
                        user_data.rut = rut
                        user_data.name = response_data.get('nombres', None)
                        user_data.lastname_1 = response_data.get('apellidoPaterno', None)
                        user_data.lastname_2 = response_data.get('apellidoMaterno', None)
                        user_data.save()
        else:
            user = user_token.user
            login(request, user)
            user_token.access_token = json_response['access_token']
            user_token.token_type = json_response['token_type']
            user_token.save()
        return HttpResponseRedirect(self.redirect_url)

    def get_user_profile(self, data, id_token):
        rut = data.get('RUT', '').replace('.', '').replace('-', '')\
                                .lower()
        # TODO: Nombre del campo de rut debería estar en settings
        profile = None
        user = None
        if PROFILE_MODEL:
            profile = PROFILE_MODEL.objects.filter(rut=rut).first()
            if profile:
                profile.name = data.get('nombres', None)
                profile.lastname_1 = data.get('apellidoPaterno', None)
                profile.lastname_2 = data.get('apellidoMaterno', None)
                try:
                    profile.rut_verified = True
                    profile.save()
                except:
                    pass
                return profile.user, profile

        if not profile:
            user = USER_MODEL.objects.get_or_create(username=rut)[0]
            if not user:
                # TODO: Campo username desde settings
                user = USER_MODEL.objects.create()
                user.set_password(id_token)

            if PROFILE_MODEL:
                profile, created = PROFILE_MODEL.objects\
                                                .get_or_create(user=user)
                if created or not profile.rut:
                    profile.rut = rut
                    profile.name = data.get('nombres', None)
                    profile.lastname_1 = data.get('apellidoPaterno', None)
                    profile.lastname_2 = data.get('apellidoMaterno', None)
                    try:
                        profile.rut_verified = True
                    except:
                        pass
                    profile.save()
            else:
                profile = None

        return user, profile
