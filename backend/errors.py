from flask import jsonify
from database.db import db

# 1. Creamos nuestra propia "Alarma" personalizada
class APIError(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message
        return rv

# 2. Creamos el "Cazador" que atrapa las alarmas y los fallos inesperados
def register_error_handlers(app):
    

    @app.errorhandler(APIError)
    def handle_api_error(error):
        db.session.rollback() 
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    # Este atrapa CUALQUIER otro error de Python/SQL (ej: fallos de sintaxis, caídas de BD)
    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback() # CRÍTICO: Limpia la BD si hubo fallo
        
        # Aquí podrías guardar el error en tu tabla de Logs en el futuro
        print(f" ERROR CRÍTICO NO CONTROLADO: {error}") 
        
        response = jsonify({
            "status": "error",
            "message": "Error interno del servidor. Revisa los logs."
        })
        response.status_code = 500
        return response