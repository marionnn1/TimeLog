from flask import jsonify
from database.db import db

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

def register_error_handlers(app):
    

    @app.errorhandler(APIError)
    def handle_api_error(error):
        db.session.rollback() 
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback() 
        print(f" ERROR CRÍTICO NO CONTROLADO: {error}") 
        
        response = jsonify({
            "status": "error",
            "message": "Error interno del servidor. Revisa los logs."
        })
        response.status_code = 500
        return response