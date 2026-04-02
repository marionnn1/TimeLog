from flask import Blueprint, jsonify, request, g
from auth import require_auth
from services.manager.projects_service import (
    get_all_projects_data, save_project, eliminar_proyecto_fisico, 
    cambiar_estado_proyecto, assign_user, unassign_user, save_client, update_client, delete_client
)

manager_projects_bp = Blueprint('manager_projects', __name__, url_prefix='/api/manager/projects')

@manager_projects_bp.route('', methods=['GET'], strict_slashes=False)
@manager_projects_bp.route('/', methods=['GET'], strict_slashes=False)
@require_auth
def get_projects():
    data = get_all_projects_data()
    return jsonify({"status": "success", "data": data}), 200

@manager_projects_bp.route('', methods=['POST'], strict_slashes=False)
@manager_projects_bp.route('/', methods=['POST'], strict_slashes=False)
@require_auth
def create_project():
    save_project(request.get_json())
    return jsonify({"status": "success", "message": "Proyecto guardado correctamente"}), 200

@manager_projects_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
@require_auth
def update_project(id):
    save_project(request.get_json(), id)
    return jsonify({"status": "success", "message": "Proyecto actualizado correctamente"}), 200

@manager_projects_bp.route('/<int:id>/force', methods=['DELETE'], strict_slashes=False)
@require_auth
def delete_project(id):
    eliminar_proyecto_fisico(id)
    return jsonify({"status": "success", "message": "Proyecto eliminado"}), 200

@manager_projects_bp.route('/<int:id>/estado', methods=['PUT'], strict_slashes=False)
@require_auth
def change_estado_proyecto(id):
    nuevo_estado = request.json.get('estado')
    cambiar_estado_proyecto(id, nuevo_estado)
    return jsonify({"status": "success", "message": f"Estado actualizado a {nuevo_estado}"}), 200

@manager_projects_bp.route('/<int:id>/assign', methods=['POST'], strict_slashes=False)
@require_auth
def assign(id):
    body = request.get_json()
    assign_user(id, body.get('usuarioId'))
    return jsonify({"status": "success", "message": "Usuario asignado"}), 200

@manager_projects_bp.route('/<int:id>/unassign', methods=['POST'], strict_slashes=False)
@require_auth
def unassign(id):
    body = request.get_json()
    unassign_user(id, body.get('usuarioId'))
    return jsonify({"status": "success", "message": "Usuario quitado del proyecto"}), 200

@manager_projects_bp.route('/clients', methods=['POST'], strict_slashes=False)
@require_auth
def create_client():
    save_client(request.get_json())
    return jsonify({"status": "success", "message": "Cliente creado correctamente"}), 200

@manager_projects_bp.route('/clients/<int:id>', methods=['PUT'], strict_slashes=False)
@require_auth
def update_client_route(id):
    update_client(id, request.get_json())
    return jsonify({"status": "success", "message": "Cliente actualizado correctamente"}), 200

@manager_projects_bp.route('/clients/<int:id>', methods=['DELETE'], strict_slashes=False)
@require_auth
def delete_client_route(id):
    delete_client(id)
    return jsonify({"status": "success", "message": "Cliente eliminado correctamente"}), 200