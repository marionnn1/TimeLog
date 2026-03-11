from flask import Blueprint, request, jsonify
from TimeLog.backend.services.admin.projects_service import (
    get_projects, 
    create_project, 
    update_project, 
    hard_delete_project, 
    toggle_project_status
)

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/admin/projects', methods=['GET'])
def get_all():
    projects = get_projects()
    if projects is not None:
        return jsonify({"status": "success", "data": projects}), 200
    return jsonify({"status": "error", "message": "Error connecting to the DB"}), 500

@projects_bp.route('/api/admin/projects', methods=['POST'])
def create():
    if create_project(request.json):
        return jsonify({"status": "success", "message": "Project created"}), 201
    return jsonify({"status": "error", "message": "Failed to create project"}), 500

@projects_bp.route('/api/admin/projects/<int:project_id>', methods=['PUT'])
def update(project_id):
    if update_project(project_id, request.json):
        return jsonify({"status": "success", "message": "Project updated"}), 200
    return jsonify({"status": "error", "message": "Failed to update project"}), 500

@projects_bp.route('/api/admin/projects/<int:project_id>/force', methods=['DELETE'])
def delete_permanent(project_id):
    if hard_delete_project(project_id):
        return jsonify({"status": "success", "message": "Project permanently deleted from DB"}), 200
    return jsonify({
        "status": "error", 
        "message": "Cannot delete from DB: project has linked data"
    }), 500

@projects_bp.route('/api/admin/projects/<int:project_id>/toggle', methods=['PUT'])
def toggle_project(project_id):
    if toggle_project_status(project_id):
        return jsonify({"status": "success", "message": "Project status updated"}), 200
    return jsonify({"status": "error", "message": "Could not change status"}), 500