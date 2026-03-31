import os
import jwt
import requests
from functools import wraps
from flask import request, g
from errors import APIError
from models.users import Users
from dotenv import load_dotenv

load_dotenv()

TENANT_ID = os.getenv("MSAL_TENANT_ID")
CLIENT_ID = os.getenv("MSAL_CLIENT_ID")


def get_public_keys():
    """Obtiene las llaves públicas de Microsoft para verificar la firma del token."""
    jwks_url = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
    return requests.get(jwks_url).json()


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)

        if not auth_header:
            raise APIError("Cabecera Authorization no encontrada", status_code=401)

        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            raise APIError(
                "La cabecera debe tener el formato 'Bearer <token>'", status_code=401
            )

        token = parts[1]

        try:
            unverified_header = jwt.get_unverified_header(token)
            jwks = get_public_keys()

            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"],
                    }
                    break

            if not rsa_key:
                raise APIError(
                    "No se encontró una llave pública válida en Azure", status_code=401
                )

            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_aud": False, "verify_issuer": False},
            )

            oid_azure = payload.get("oid")
            usuario = Users.query.filter_by(oid_azure=oid_azure).first()

            if not usuario or not usuario.activo:
                raise APIError(
                    "Usuario no autorizado o desactivado en la BD", status_code=403
                )

            g.usuario_actual = usuario

        except jwt.ExpiredSignatureError:
            raise APIError("El token de Microsoft ha caducado", status_code=401)
        except Exception as e:
            print(f"Error descodificando token: {str(e)}")
            raise APIError(f"Token inválido: {str(e)}", status_code=401)

        return f(*args, **kwargs)

    return decorated
