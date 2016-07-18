# -*- coding: utf-8 -*-
u"""
Conjunto de decoradores para crear datos de sesión o autenticación necesarios
para hacer funcionar ClaveUnica.
Pueden ser llamados como cualquier otro decorador de Django.
"""
from .middleware import ClAuthMiddleware
from django.utils.decorators import decorator_from_middleware

# Crea un token para el registro con ClaveUnica y lo agrega a los datos
# de sesión.
cl_auth_view = decorator_from_middleware(ClAuthMiddleware)
