from flask import Blueprint, request, jsonify
from auth import token_required
from services.technical.time_entries_user_service import obtener_imputaciones_semana, guardar_imputaciones_lote
from errors import APIError

time_entries_user_bp = Blueprint('time_entries_user', __name__)

@time_entries_user_bp.route('/api/imputaciones/semana', methods=['GET'])
@token_required
def get_semana():
    u_id = request.args.get('usuario_id')
    lunes = request.args.get('fecha_lunes')
    
    if not u_id or not lunes:
        raise APIError("Faltan parámetros obligatorios: usuario_id o fecha_lunes", status_code=400)
        
    res = obtener_imputaciones_semana(u_id, lunes)
    return jsonify({"status": "success", "data": res}), 200

@time_entries_user_bp.route('/api/imputaciones/guardar', methods=['POST'])
@token_required
def save_lote():
    data = request.json
    if not data:
        raise APIError("No se enviaron datos en la petición", status_code=400)
        
    guardar_imputaciones_lote(data.get('usuario_id'), data.get('filas'), data.get('fechas'))
    return jsonify({"status": "success", "message": "Imputaciones guardadas correctamente"}), 200