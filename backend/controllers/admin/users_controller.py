from flask import Blueprint, request, jsonify
from services.admin.users_service import (
    toggle_estado_usuario, obtener_usuarios, crear_usuario, 
    actualizar_usuario, eliminar_usuario, eliminar_usuario_fisico
)

from services.admin.users_service import (
    toggle_estado_usuario, obtener_usuarios, crear_usuario, 
    actualizar_usuario, eliminar_usuario, eliminar_usuario_fisico,
    sync_usuario_sso
)

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/usuarios', methods=['GET'])
def get_all():
    usuarios = obtener_usuarios()
    return jsonify({"status": "success", "data": usuarios}), 200

@users_bp.route('/api/usuarios', methods=['POST'])
def create():
    crear_usuario(request.json)
    return jsonify({"status": "success", "message": "Usuario creado"}), 201

@users_bp.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
def update(id_usuario):
    actualizar_usuario(id_usuario, request.json)
    return jsonify({"status": "success", "message": "Usuario actualizado"}), 200

@users_bp.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def deactivate(id_usuario):
    eliminar_usuario(id_usuario)
    return jsonify({"status": "success", "message": "Usuario desactivado correctamente"}), 200

@users_bp.route('/api/usuarios/<int:id_usuario>/force', methods=['DELETE'])
def delete_permanent(id_usuario):
    eliminar_usuario_fisico(id_usuario)
    return jsonify({"status": "success", "message": "Usuario eliminado permanentemente de la BD"}), 200

@users_bp.route('/api/usuarios/<int:id_usuario>/toggle', methods=['PUT'])
def toggle_usuario(id_usuario):
    toggle_estado_usuario(id_usuario)
    return jsonify({"status": "success", "message": "Estado del usuario actualizado"}), 200

@users_bp.route('/api/usuarios/sync', methods=['POST'])
def sync_endpoint():
    data = sync_usuario_sso(request.json)
    return jsonify({"status": "success", "data": data}), 200