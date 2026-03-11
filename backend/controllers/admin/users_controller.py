from flask import Blueprint, request, jsonify
from TimeLog.backend.services.admin.users_service import (
    get_users, 
    create_user, 
    update_user, 
    delete_user,         
    hard_delete_user,    
    toggle_user_status
)

# We create the routes blueprint for users
users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['GET'])
def get_all():
    users = get_users()
    if users is not None:
        return jsonify({"status": "success", "data": users}), 200
    return jsonify({"status": "error", "message": "Error connecting to the DB"}), 500

@users_bp.route('/api/users', methods=['POST'])
def create():
    if create_user(request.json):
        return jsonify({"status": "success", "message": "User created"}), 201
    return jsonify({"status": "error", "message": "Failed to create user"}), 500

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update(user_id):
    if update_user(user_id, request.json):
        return jsonify({"status": "success", "message": "User updated"}), 200
    return jsonify({"status": "error", "message": "Failed to update user"}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def deactivate(user_id):
    if delete_user(user_id):
        return jsonify({"status": "success", "message": "User deactivated successfully"}), 200
    return jsonify({"status": "error", "message": "Failed to deactivate user"}), 500


@users_bp.route('/api/users/<int:user_id>/force', methods=['DELETE'])
def delete_permanent(user_id):
    if hard_delete_user(user_id):
        return jsonify({"status": "success", "message": "User permanently deleted from DB"}), 200
    return jsonify({
        "status": "error", 
        "message": "Cannot delete from DB: the user has linked data (time entries or projects)"
    }), 500

@users_bp.route('/api/users/<int:user_id>/toggle', methods=['PUT'])
def toggle_user(user_id):
    success = toggle_user_status(user_id)
    if success:
        return jsonify({"status": "success", "message": "User status updated"}), 200
    return jsonify({"status": "error", "message": "Could not change status"}), 500