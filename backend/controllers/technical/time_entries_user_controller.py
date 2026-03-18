from flask import Blueprint, request, jsonify
# Añadimos _service para que coincida con el nombre de tu archivo
from services.technical.time_entries_user_service import obtener_imputaciones_semana, guardar_imputaciones_lote
time_entries_user_bp = Blueprint('time_entries_user', __name__)

@time_entries_user_bp.route('/api/imputaciones/semana', methods=['GET'])
def get_semana():
    u_id = request.args.get('usuario_id')
    lunes = request.args.get('fecha_lunes')
    
    if not u_id or not lunes:
        return jsonify({"status": "error", "message": "Faltan parámetros"}), 400
        
    res = obtener_imputaciones_semana(u_id, lunes)
    if res is not None:
        return jsonify({"status": "success", "data": res}), 200
    return jsonify({"status": "error", "message": "Error al consultar la BD"}), 500

@time_entries_user_bp.route('/api/imputaciones/guardar', methods=['POST'])
def save_lote():
    data = request.json
    exito = guardar_imputaciones_lote(data['usuario_id'], data['filas'], data['fechas'])
    if exito:
        return jsonify({"status": "success", "message": "Imputaciones guardadas"}), 200
    return jsonify({"status": "error", "message": "Fallo al guardar"}), 500