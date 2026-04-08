import os
import jwt
import requests
import time
from functools import wraps
from flask import request, g
from errors import APIError
from models.users import Users
from database.db import db
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("MSAL_TENANT_ID")
CLIENT_ID = os.getenv("MSAL_CLIENT_ID")

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
        if cached_jwks:
            return cached_jwks
        raise e


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
            rsa_key = next(
                (k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None
            )

            if not rsa_key:
                raise APIError("Firma de Azure no reconocida", status_code=401)

            from jwt.algorithms import RSAAlgorithm

            public_key = RSAAlgorithm.from_jwk(rsa_key)

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            )

            oid_azure = payload.get("oid")
            usuario = Users.query.filter_by(oid_azure=oid_azure).first()

            if not usuario or not usuario.activo:
                raise APIError("Usuario no autorizado o desactivado", status_code=403)

            roles_azure = payload.get("roles")

            if not roles_azure or len(roles_azure) == 0:
                raise APIError(
                    "Tu usuario no tiene un rol configurado en Azure AD. Acceso bloqueado.",
                    status_code=403,
                )

            rol_principal_azure = roles_azure[0]

            if usuario.rol != rol_principal_azure:
                usuario.rol = rol_principal_azure
                db.session.commit()

            g.usuario_actual = usuario
            g.token_payload = payload

        except jwt.ExpiredSignatureError:
            raise APIError("La sesión de Microsoft ha caducado", status_code=401)
        except jwt.InvalidAudienceError:
            raise APIError("Token no generado para esta aplicación", status_code=401)
        except jwt.InvalidIssuerError:
            raise APIError("Emisor del token no válido", status_code=401)
        except Exception as e:
            print("Error:", flush=True)
            print(e, flush=True)
            raise APIError(f"Token inválido: {str(e)}", status_code=401)

        return f(*args, **kwargs)

    return decorated


def require_role(roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            payload = getattr(g, "token_payload", {})

            roles_azure = payload.get("roles")
            if not roles_azure:
                raise APIError(
                    "Acceso denegado. Azure no reporta ningún rol para este usuario.",
                    status_code=403,
                )

            roles_usuario_norm = [r.lower() for r in roles_azure]
            roles_permitidos_norm = [r.lower() for r in roles_permitidos]

            tiene_permiso = any(
                rol in roles_permitidos_norm for rol in roles_usuario_norm
            )

            if not tiene_permiso:
                raise APIError(
                    f"Acceso denegado. Se requiere uno de estos roles: {roles_permitidos}",
                    status_code=403,
                )

            return f(*args, **kwargs)

        return decorated

    return decorator
