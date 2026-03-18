from flask import Blueprint, request, jsonify
from services.technical.absences_service import obtener_ausencias_mes, guardar_ausencias, eliminar_ausencia
from datetime import datetime

absences_bp = Blueprint('absences', __name__)

@absences_bp.route('/api/absences', methods=['GET'])
def get_ausencias():
    try:
        mes = int(request.args.get('mes', datetime.now().month))
        anio = int(request.args.get('anio', datetime.now().year))
    except (ValueError, TypeError):
        mes = datetime.now().month
        anio = datetime.now().year
        
    data = obtener_ausencias_mes(mes, anio)
    return jsonify({"status": "success", "data": data})

@absences_bp.route('/api/absences', methods=['POST'])
def create_ausencias():
    d = request.json
    if not d: return jsonify({"status": "error"}), 400
    
    exito = guardar_ausencias(d.get('usuario_id'), d.get('fechas'), d.get('tipo'), d.get('comentario', ''))
    return jsonify({"status": "success" if exito else "error"}), 200 if exito else 500

@absences_bp.route('/api/absences', methods=['DELETE'])
def delete_ausencia():
    d = request.json
    if not d: return jsonify({"status": "error"}), 400
    
    exito = eliminar_ausencia(d.get('usuario_id'), d.get('fecha'))
    return jsonify({"status": "success" if exito else "error"}), 200 if exito else 500