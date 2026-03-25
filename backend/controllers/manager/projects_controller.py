from flask import Blueprint, request
from services.manager.projects_service import (
    get_all_projects_data, save_project, soft_delete_project, 
    assign_user, unassign_user, save_client, update_client, delete_client
)
from utils.responses import success_response

manager_projects_bp = Blueprint('manager_projects', __name__, url_prefix='/api/manager/projects')

@manager_projects_bp.route('', methods=['GET'], strict_slashes=False)
@manager_projects_bp.route('/', methods=['GET'], strict_slashes=False)
def get_projects():
    return success_response(data=get_all_projects_data())

@manager_projects_bp.route('', methods=['POST'], strict_slashes=False)
@manager_projects_bp.route('/', methods=['POST'], strict_slashes=False)
def create_project():
    return success_response(data=save_project(request.get_json()), status_code=201)

@manager_projects_bp.route('/<int:id>', methods=['PUT'], strict_slashes=False)
def update_project(id):
    return success_response(data=save_project(request.get_json(), id))

@manager_projects_bp.route('/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_project(id):
    return success_response(data=soft_delete_project(id))

@manager_projects_bp.route('/<int:id>/assign', methods=['POST'], strict_slashes=False)
def assign(id):
    return success_response(data=assign_user(id, request.get_json().get('usuarioId')))

@manager_projects_bp.route('/<int:id>/unassign', methods=['POST'], strict_slashes=False)
def unassign(id):
    return success_response(data=unassign_user(id, request.get_json().get('usuarioId')))

@manager_projects_bp.route('/clients', methods=['POST'], strict_slashes=False)
def create_client():
    return success_response(data=save_client(request.get_json()), status_code=201)

@manager_projects_bp.route('/clients/<int:id>', methods=['PUT'], strict_slashes=False)
def update_client_route(id):
    return success_response(data=update_client(id, request.get_json()))

@manager_projects_bp.route('/clients/<int:id>', methods=['DELETE'], strict_slashes=False)
def delete_client_route(id):
    return success_response(data=delete_client(id))