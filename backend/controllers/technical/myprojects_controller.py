from flask import Blueprint, request, jsonify
from services.technical.myprojects_service import solicitar_correccion_imputacion
from services.technical.myprojects_service import (
    obtener_imputaciones_semana, 
    guardar_imputaciones_lote, 
    obtener_analitica_mensual,
    obtener_analitica_equipo,
    obtener_calendario_mensual
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
    try:
        mes = int(request.args.get('mes', datetime.now().month))
        anio = int(request.args.get('anio', datetime.now().year))
    except (ValueError, TypeError):
        mes, anio = datetime.now().month, datetime.now().year

    data = obtener_analitica_mensual(u_id, mes, anio)
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/analitica-equipo', methods=['GET'])
def get_analitica_equipo():
    try:
        mes = int(request.args.get('mes', datetime.now().month))
        anio = int(request.args.get('anio', datetime.now().year))
    except (ValueError, TypeError):
        mes, anio = datetime.now().month, datetime.now().year

    data = obtener_analitica_equipo(mes, anio)
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/guardar', methods=['POST'])
def save():
    d = request.json
    if not d: return jsonify({"status": "error"}), 400
    exito = guardar_imputaciones_lote(d.get('usuario_id'), d.get('filas'), d.get('fechas'))
    return jsonify({"status": "success" if exito else "error"}), 200 if exito else 500

@myprojects_bp.route('/api/myprojects/calendario', methods=['GET'])
def get_calendario():
    u_id = request.args.get('usuario_id')
    mes = request.args.get('mes')
    anio = request.args.get('anio')
    
    if not all([u_id, mes, anio]):
        return jsonify({"status": "error", "message": "Faltan parámetros"}), 400
        
    data = obtener_calendario_mensual(u_id, int(mes), int(anio))
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/solicitar-correccion', methods=['POST'])
def solicitar_correccion():
    data = request.json
    if not data: 
        return jsonify({"status": "error", "message": "Datos vacíos"}), 400

    usuario_id = data.get('usuario_id')
    proyecto_id = data.get('proyecto_id')
    fecha = data.get('fecha')
    nuevas_horas = data.get('nuevas_horas')
    motivo = data.get('motivo')

    if not all([usuario_id, proyecto_id, fecha, nuevas_horas is not None, motivo]):
        return jsonify({"status": "error", "message": "Faltan datos obligatorios"}), 400

    exito = solicitar_correccion_imputacion(usuario_id, proyecto_id, fecha, nuevas_horas, motivo)

    if exito:
        return jsonify({"status": "success", "message": "Solicitud enviada al responsable"}), 200
    return jsonify({"status": "error", "message": "Fallo al enviar la solicitud"}), 500