from flask import jsonify

def success_response(data=None, message="Operación exitosa", status_code=200):
    """
    Formato estándar para todas las respuestas correctas de la API.
    """
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data
        
    return jsonify(response), status_code

def error_response(message="Error interno del servidor", status_code=500):
    """
    Formato estándar para todos los errores de la API.
    """
    return jsonify({
        "status": "error",
        "message": message
    }), status_code