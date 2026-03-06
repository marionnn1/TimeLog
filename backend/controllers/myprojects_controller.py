from flask import Blueprint, request, jsonify
from services.myprojects_service import (
    obtener_imputaciones_semana, 
    guardar_imputaciones_lote, 
    obtener_analitica_mensual
)
from datetime import datetime

myprojects_bp = Blueprint('myprojects', __name__)

@myprojects_bp.route('/api/myprojects/semana', methods=['GET'])
def get_semana():
    u_id = request.args.get('usuario_id')
    lunes = request.args.get('fecha_lunes')
    return jsonify({"status": "success", "data": obtener_imputaciones_semana(u_id, lunes)})

@myprojects_bp.route('/api/myprojects/analitica-mensual', methods=['GET'])
def get_analitica():
    u_id = request.args.get('usuario_id')
    # Validamos y convertimos parámetros
    try:
        mes = int(request.args.get('mes', datetime.now().month))
        anio = int(request.args.get('anio', datetime.now().year))
    except (ValueError, TypeError):
        mes, anio = datetime.now().month, datetime.now().year

    data = obtener_analitica_mensual(u_id, mes, anio)
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/guardar', methods=['POST'])
def save():
    d = request.json
    if not d: return jsonify({"status": "error"}), 400
    exito = guardar_imputaciones_lote(d.get('usuario_id'), d.get('filas'), d.get('fechas'))
    return jsonify({"status": "success" if exito else "error"}), 200 if exito else 500