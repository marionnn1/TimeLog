from flask import Blueprint, jsonify, request
from services.manager.projects_service import (
    get_all_projects_data, save_project, soft_delete_project, 
    assign_user, unassign_user, save_client, update_client, delete_client
)

manager_projects_bp = Blueprint('manager_projects', __name__, url_prefix='/api/manager/projects')

@manager_projects_bp.route('', methods=['GET'], strict_slashes=False)
@manager_projects_bp.route('/', methods=['GET'], strict_slashes=False)
def get_projects():
    data, status = get_all_projects_data()
    return jsonify(data), status

@manager_projects_bp.route('', methods=['POST'], strict_slashes=False)
@manager_projects_bp.route('/', methods=['POST'], strict_slashes=False)
def create_project():
    data, status = save_project(request.get_json())
    return jsonify(data), status

@manager_projects_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
def update_project(id):
    data, status = save_project(request.get_json(), id)
    return jsonify(data), status

@manager_projects_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_project(id):
    data, status = soft_delete_project(id)
    return jsonify(data), status

@manager_projects_bp.route('/<int:id>/assign', methods=['POST'], strict_slashes=False)
def assign(id):
    body = request.get_json()
    data, status = assign_user(id, body.get('usuarioId'))
    return jsonify(data), status

@manager_projects_bp.route('/<int:id>/unassign', methods=['POST'], strict_slashes=False)
def unassign(id):
    body = request.get_json()
    data, status = unassign_user(id, body.get('usuarioId'))
    return jsonify(data), status

@manager_projects_bp.route('/clients', methods=['POST'], strict_slashes=False)
def create_client():
    data, status = save_client(request.get_json())
    return jsonify(data), status

@manager_projects_bp.route('/clients/<int:id>', methods=['PUT'], strict_slashes=False)
def update_client_route(id):
    data, status = update_client(id, request.get_json())
    return jsonify(data), status

@manager_projects_bp.route('/clients/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_client_route(id):
    data, status = delete_client(id)
    return jsonify(data), status