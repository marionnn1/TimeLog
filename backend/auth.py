import os
import jwt
import requests
import time
from functools import wraps
from flask import request, g
from errors import APIError
from models.users import Users
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("MSAL_TENANT_ID")
CLIENT_ID = os.getenv("MSAL_CLIENT_ID")

# --- CACHÉ DE LLAVES (Mantenemos tu mejora anterior) ---
cached_jwks = None
last_jwks_fetch = 0
JWKS_CACHE_DURATION = 43200 

def get_public_keys():
    global cached_jwks, last_jwks_fetch
    current_time = time.time()
    if cached_jwks and (current_time - last_jwks_fetch < JWKS_CACHE_DURATION):
        return cached_jwks
    jwks_url = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
    try:
        response = requests.get(jwks_url, timeout=5)
        cached_jwks = response.json()
        last_jwks_fetch = current_time
        return cached_jwks
    except Exception as e:
        if cached_jwks: return cached_jwks
        raise e

# --- DECORADOR DE AUTENTICACIÓN ---
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            raise APIError("Cabecera Authorization no encontrada", status_code=401)

        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            raise APIError("Formato de token inválido", status_code=401)

        token = parts[1]
        try:
            unverified_header = jwt.get_unverified_header(token)
            jwks = get_public_keys()
            rsa_key = next((k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None)
            
            if not rsa_key:
                raise APIError("Firma de Azure no reconocida", status_code=401)

            from jwt.algorithms import RSAAlgorithm
            public_key = RSAAlgorithm.from_jwk(rsa_key)
            payload = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False, "verify_issuer": False})

            oid_azure = payload.get("oid")
            usuario = Users.query.filter_by(oid_azure=oid_azure).first()

            if not usuario or not usuario.activo:
                raise APIError("Usuario no autorizado o desactivado", status_code=403)

            # Guardamos el objeto usuario completo para usarlo en los controladores
            g.usuario_actual = usuario 

        except jwt.ExpiredSignatureError:
            raise APIError("La sesión de Microsoft ha caducado", status_code=401)
        except Exception as e:
            raise APIError(f"Token inválido: {str(e)}", status_code=401)

        return f(*args, **kwargs)
    return decorated

# --- NUEVO DECORADOR DE ROLES (RBAC) ---
def require_role(roles_permitidos):
    """
    Verifica que el usuario tenga uno de los roles permitidos.
    Uso: @require_role(['Admin', 'JP'])
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Validamos que g.usuario_actual exista (require_auth debe ir antes)
            usuario = getattr(g, 'usuario_actual', None)
            if not usuario:
                raise APIError("Error de seguridad: Usuario no identificado", status_code=500)
            
            # Normalizamos roles para evitar errores de mayúsculas/minúsculas
            rol_actual = usuario.rol.lower() if usuario.rol else ""
            roles_lista = [r.lower() for r in roles_permitidos]

            if rol_actual not in roles_lista:
                raise APIError(f"Acceso denegado. Se requiere uno de estos roles: {roles_permitidos}", status_code=403)
            
            return f(*args, **kwargs)
        return decorated
    return decorator