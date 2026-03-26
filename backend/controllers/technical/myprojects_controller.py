from flask import Blueprint, request, jsonify
from services.technical.myprojects_service import (
    obtener_imputaciones_semana, 
    guardar_imputaciones_lote, 
    obtener_analitica_mensual,
    obtener_analitica_equipo,
    obtener_calendario_mensual,
    solicitar_correccion_imputacion,
    obtener_jornada,
    actualizar_jornada,
    obtener_proyectos_asignados
)
from datetime import datetime
from errors import APIError

myprojects_bp = Blueprint('myprojects', __name__)

@myprojects_bp.route('/api/myprojects/semana', methods=['GET'])
def get_semana():
    u_id = request.args.get('usuario_id')
    lunes = request.args.get('fecha_lunes')
    
    if not u_id or not lunes:
        raise APIError("Faltan parámetros", status_code=400)
        
    data = obtener_imputaciones_semana(u_id, lunes)
    return jsonify({"status": "success", "data": data}), 200

@myprojects_bp.route('/api/myprojects/analitica-mensual', methods=['GET'])
def get_analitica():
    u_id = request.args.get('usuario_id')
    if not u_id:
        raise APIError("Falta usuario_id", status_code=400)
        
    mes = request.args.get('mes', datetime.now().month, type=int)
    anio = request.args.get('anio', datetime.now().year, type=int)

    data = obtener_analitica_mensual(u_id, mes, anio)
    return jsonify({"status": "success", "data": data}), 200

@myprojects_bp.route('/api/myprojects/analitica-equipo', methods=['GET'])
def get_analitica_equipo():
    mes = request.args.get('mes', datetime.now().month, type=int)
    anio = request.args.get('anio', datetime.now().year, type=int)

    data = obtener_analitica_equipo(mes, anio)
    return jsonify({"status": "success", "data": data}), 200

@myprojects_bp.route('/api/myprojects/guardar', methods=['POST'])
def save():
    d = request.json
    if not d: 
        raise APIError("Petición vacía", status_code=400)
        
    guardar_imputaciones_lote(d.get('usuario_id'), d.get('filas'), d.get('fechas'))
    return jsonify({"status": "success", "message": "Imputaciones guardadas correctamente"}), 200

@myprojects_bp.route('/api/myprojects/calendario', methods=['GET'])
def get_calendario():
    u_id = request.args.get('usuario_id')
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)
    
    if not all([u_id, mes, anio]):
        raise APIError("Faltan parámetros", status_code=400)
        
    data = obtener_calendario_mensual(u_id, mes, anio)
    return jsonify({"status": "success", "data": data}), 200

@myprojects_bp.route('/api/myprojects/solicitar-correccion', methods=['POST'])
def solicitar_correccion():
    data = request.json
    if not data: 
        raise APIError("Datos vacíos", status_code=400)

    usuario_id = data.get('usuario_id')
    proyecto_id = data.get('proyecto_id')
    fecha = data.get('fecha')
    nuevas_horas = data.get('nuevas_horas')
    motivo = data.get('motivo')

    if not all([usuario_id, proyecto_id, fecha, nuevas_horas is not None, motivo]):
        raise APIError("Faltan datos obligatorios", status_code=400)

    solicitar_correccion_imputacion(usuario_id, proyecto_id, fecha, nuevas_horas, motivo)
    return jsonify({"status": "success", "message": "Solicitud enviada al responsable"}), 200

@myprojects_bp.route('/api/myprojects/jornada', methods=['GET'])
def get_user_jornada():
    u_id = request.args.get('usuario_id')
    if not u_id:
        raise APIError("Falta usuario_id", status_code=400)
        
    data = obtener_jornada(u_id)
    return jsonify({"status": "success", "data": data}), 200

@myprojects_bp.route('/api/myprojects/jornada', methods=['PUT'])
def update_user_jornada():
    data = request.json
    if not data or 'usuario_id' not in data:
        raise APIError("Datos inválidos", status_code=400)
        
    actualizar_jornada(data.get('usuario_id'), data)
    return jsonify({"status": "success", "message": "Jornada actualizada"}), 200

@myprojects_bp.route('/api/myprojects/asignados', methods=['GET'])
def get_proyectos_asignados_endpoint():
    u_id = request.args.get('usuario_id')
    if not u_id:
        raise APIError("Falta usuario_id", status_code=400)
        
    data = obtener_proyectos_asignados(u_id)
    return jsonify({"status": "success", "data": data}), 200