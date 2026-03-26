from flask import Blueprint, request, jsonify
from services.admin.projects_service import (
    obtener_proyectos, crear_proyecto, actualizar_proyecto, eliminar_proyecto_fisico, 
    toggle_estado_proyecto, obtener_clientes, crear_cliente, actualizar_cliente, eliminar_cliente
)
from errors import APIError

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/proyectos', methods=['GET'])
def get_all():
    proyectos = obtener_proyectos()
    return jsonify({"status": "success", "data": proyectos}), 200

@projects_bp.route('/api/proyectos', methods=['POST'])
def create():
    crear_proyecto(request.json)
    return jsonify({"status": "success", "message": "Proyecto creado"}), 201

@projects_bp.route('/api/proyectos/<int:id_proyecto>', methods=['PUT'])
def update(id_proyecto):
    actualizar_proyecto(id_proyecto, request.json)
    return jsonify({"status": "success", "message": "Proyecto actualizado"}), 200

@projects_bp.route('/api/proyectos/<int:id_proyecto>/force', methods=['DELETE'])
def delete_permanent(id_proyecto):
    eliminar_proyecto_fisico(id_proyecto)
    return jsonify({"status": "success", "message": "Proyecto eliminado permanentemente de la BD"}), 200

@projects_bp.route('/api/proyectos/<int:id_proyecto>/toggle', methods=['PUT'])
def toggle_proyecto(id_proyecto):
    toggle_estado_proyecto(id_proyecto)
    return jsonify({"status": "success", "message": "Estado del proyecto actualizado"}), 200

@projects_bp.route('/api/clientes', methods=['GET'])
def get_clients():
    clientes = obtener_clientes()
    return jsonify({"status": "success", "data": clientes}), 200

@projects_bp.route('/api/clientes', methods=['POST'])
def create_client():
    crear_cliente(request.json)
    return jsonify({"status": "success", "message": "Cliente creado"}), 201

@projects_bp.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
def update_client(id_cliente):
    actualizar_cliente(id_cliente, request.json)
    return jsonify({"status": "success", "message": "Cliente actualizado"}), 200

@projects_bp.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
def delete_client(id_cliente):
    eliminar_cliente(id_cliente)
    return jsonify({"status": "success", "message": "Cliente eliminado"}), 200