from flask import Blueprint, request, jsonify
from services.admin.projects_service import (
    obtener_proyectos, 
    crear_proyecto, 
    actualizar_proyecto, 
    eliminar_proyecto_fisico, 
    toggle_estado_proyecto
)

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/proyectos', methods=['GET'])
def get_all():
    proyectos = obtener_proyectos()
    if proyectos is not None:
        return jsonify({"status": "success", "data": proyectos}), 200
    return jsonify({"status": "error", "message": "Error al conectar con la BD"}), 500

@projects_bp.route('/api/proyectos', methods=['POST'])
def create():
    if crear_proyecto(request.json):
        return jsonify({"status": "success", "message": "Proyecto creado"}), 201
    return jsonify({"status": "error", "message": "Fallo al crear el proyecto"}), 500

@projects_bp.route('/api/proyectos/<int:id_proyecto>', methods=['PUT'])
def update(id_proyecto):
    if actualizar_proyecto(id_proyecto, request.json):
        return jsonify({"status": "success", "message": "Proyecto actualizado"}), 200
    return jsonify({"status": "error", "message": "Fallo al actualizar el proyecto"}), 500

@projects_bp.route('/api/proyectos/<int:id_proyecto>/force', methods=['DELETE'])
def delete_permanent(id_proyecto):
    if eliminar_proyecto_fisico(id_proyecto):
        return jsonify({"status": "success", "message": "Proyecto eliminado permanentemente de la BD"}), 200
    return jsonify({
        "status": "error", 
        "message": "No se puede eliminar de la BD: el proyecto tiene datos vinculados"
    }), 500

@projects_bp.route('/api/proyectos/<int:id_proyecto>/toggle', methods=['PUT'])
def toggle_proyecto(id_proyecto):
    if toggle_estado_proyecto(id_proyecto):
        return jsonify({"status": "success", "message": "Estado del proyecto actualizado"}), 200
    return jsonify({"status": "error", "message": "No se pudo cambiar el estado"}), 500
