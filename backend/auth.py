import os
import jwt
from jwt import PyJWKClient
from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return jsonify({'status': 'error', 'message': 'Falta el token de seguridad'}), 401

        try:
            tenant_id = os.getenv('AZURE_TENANT_ID')
            client_id = os.getenv('AZURE_CLIENT_ID') # <-- Volvemos a usar el Client ID
            
            jwks_url = f'https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys'
            jwks_client = PyJWKClient(jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            data = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=client_id, # <-- El token ahora va dirigido a tu aplicación
                options={"verify_issuer": False} 
            )
            
            request.user_payload = data

        except jwt.ExpiredSignatureError:
            return jsonify({'status': 'error', 'message': 'El token ha caducado. Vuelve a iniciar sesión.'}), 401
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Token inválido: {str(e)}'}), 401

        return f(*args, **kwargs)

    return decorated