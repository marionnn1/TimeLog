from flask import Blueprint, request, jsonify
from services.admin.projects_service import (
    obtener_proyectos, 
    crear_proyecto, 
    actualizar_proyecto, 
    eliminar_proyecto_fisico, 
    toggle_estado_proyecto,
    obtener_clientes,
    crear_cliente,
    actualizar_cliente,
    eliminar_cliente
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


@projects_bp.route('/api/clientes', methods=['GET'])
def get_clients():
    clientes = obtener_clientes()
    if clientes is not None:
        return jsonify({"status": "success", "data": clientes}), 200
    return jsonify({"status": "error", "message": "Error al obtener clientes"}), 500

@projects_bp.route('/api/clientes', methods=['POST'])
def create_client():
    if crear_cliente(request.json):
        return jsonify({"status": "success", "message": "Cliente creado"}), 201
    return jsonify({"status": "error", "message": "El cliente ya existe o hubo un error"}), 400

@projects_bp.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
def update_client(id_cliente):
    if actualizar_cliente(id_cliente, request.json):
        return jsonify({"status": "success", "message": "Cliente actualizado"}), 200
    return jsonify({"status": "error", "message": "Fallo al actualizar el cliente"}), 500

@projects_bp.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
def delete_client(id_cliente):
    res = eliminar_cliente(id_cliente)
    if res == True:
        return jsonify({"status": "success", "message": "Cliente eliminado"}), 200
    elif res == "TIENE_PROYECTOS":
        return jsonify({"status": "error", "message": "No puedes eliminar un cliente que tiene proyectos asignados"}), 400
    return jsonify({"status": "error", "message": "Error interno al eliminar cliente"}), 500