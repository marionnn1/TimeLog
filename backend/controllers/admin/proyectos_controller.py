from flask import Blueprint, request, jsonify
from services.admin.proyectos_service import toggle_estado_proyecto
from services.admin.proyectos_service import (
    obtener_proyectos, 
    crear_proyecto, 
    actualizar_proyecto, 
    cerrar_proyecto, 
    eliminar_proyecto_fisico
)

proyectos_bp = Blueprint('proyectos', __name__)

@proyectos_bp.route('/api/proyectos', methods=['GET'])
def get_all():
    proyectos = obtener_proyectos()
    if proyectos is not None:
        return jsonify({"status": "success", "data": proyectos}), 200
    return jsonify({"status": "error", "message": "Error al conectar con la BD"}), 500

@proyectos_bp.route('/api/proyectos', methods=['POST'])
def create():
    if crear_proyecto(request.json):
        return jsonify({"status": "success", "message": "Proyecto creado"}), 201
    return jsonify({"status": "error", "message": "Fallo al crear"}), 500

@proyectos_bp.route('/api/proyectos/<int:id_proyecto>', methods=['PUT'])
def update(id_proyecto):
    # Procesa nombre, cliente, estado y la lista usuarios_ids
    if actualizar_proyecto(id_proyecto, request.json):
        return jsonify({"status": "success", "message": "Proyecto y equipo actualizados"}), 200
    return jsonify({"status": "error", "message": "Fallo al actualizar"}), 400

@proyectos_bp.route('/api/proyectos/<int:id_proyecto>', methods=['DELETE'])
def close(id_proyecto):
    if cerrar_proyecto(id_proyecto):
        return jsonify({"status": "success", "message": "Proyecto cerrado correctamente"}), 200
    return jsonify({"status": "error", "message": "Fallo al cerrar el proyecto"}), 500

@proyectos_bp.route('/api/proyectos/<int:id_proyecto>/force', methods=['DELETE'])
def delete_permanent(id_proyecto):
    if eliminar_proyecto_fisico(id_proyecto):
        return jsonify({"status": "success", "message": "Proyecto eliminado permanentemente"}), 200
    return jsonify({
        "status": "error", 
        "message": "No se puede eliminar de la BD: tiene datos vinculados"
    }), 500

@proyectos_bp.route('/api/proyectos/<int:id_proyecto>/toggle', methods=['PUT'])
def toggle_proyecto(id_proyecto):
    from services.admin.proyectos_service import toggle_estado_proyecto # Importar arriba
    exito = toggle_estado_proyecto(id_proyecto)
    if exito:
        return jsonify({"status": "success", "message": "Estado del proyecto actualizado"}), 200
    return jsonify({"status": "error", "message": "No se pudo cambiar el estado"}), 500