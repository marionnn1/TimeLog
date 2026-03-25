from flask import Blueprint, request
from services.admin.projects_service import (
    obtener_proyectos, crear_proyecto, actualizar_proyecto, eliminar_proyecto_fisico, 
    toggle_estado_proyecto, obtener_clientes, crear_cliente, actualizar_cliente, eliminar_cliente
)
from utils.responses import success_response

# AQUÍ ESTÁ LA LÍNEA QUE FLASK NO ENCONTRABA
projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/proyectos', methods=['GET'])
def get_all():
    return success_response(data=obtener_proyectos())

@projects_bp.route('/api/proyectos', methods=['POST'])
def create():
    crear_proyecto(request.json)
    return success_response(message="Proyecto creado", status_code=201)

@projects_bp.route('/api/proyectos/<int:id_proyecto>', methods=['PUT'])
def update(id_proyecto):
    actualizar_proyecto(id_proyecto, request.json)
    return success_response(message="Proyecto actualizado")

@projects_bp.route('/api/proyectos/<int:id_proyecto>/force', methods=['DELETE'])
def delete_permanent(id_proyecto):
    eliminar_proyecto_fisico(id_proyecto)
    return success_response(message="Proyecto eliminado permanentemente de la BD")

@projects_bp.route('/api/proyectos/<int:id_proyecto>/toggle', methods=['PUT'])
def toggle_proyecto(id_proyecto):
    toggle_estado_proyecto(id_proyecto)
    return success_response(message="Estado del proyecto actualizado")

@projects_bp.route('/api/clientes', methods=['GET'])
def get_clients():
    return success_response(data=obtener_clientes())

@projects_bp.route('/api/clientes', methods=['POST'])
def create_client():
    crear_cliente(request.json)
    return success_response(message="Cliente creado", status_code=201)

@projects_bp.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
def update_client_route(id_cliente):
    actualizar_cliente(id_cliente, request.json)
    return success_response(message="Cliente actualizado")

@projects_bp.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
def delete_client_route(id_cliente):
    eliminar_cliente(id_cliente)
    return success_response(message="Cliente eliminado")