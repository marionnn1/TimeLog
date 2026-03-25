from flask import Blueprint, request
from services.admin.users_service import (
    obtener_usuarios, 
    crear_usuario, 
    actualizar_usuario, 
    eliminar_usuario,
    eliminar_usuario_fisico,
    toggle_estado_usuario
)
from utils.responses import success_response

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/usuarios', methods=['GET'])
def get_all():
    usuarios = obtener_usuarios()
    return success_response(data=usuarios, message="Usuarios cargados")

@users_bp.route('/api/usuarios', methods=['POST'])
def create():
    crear_usuario(request.json)
    return success_response(message="Usuario creado correctamente", status_code=201)

@users_bp.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
def update(id_usuario):
    actualizar_usuario(id_usuario, request.json)
    return success_response(message="Usuario actualizado correctamente")

@users_bp.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def deactivate(id_usuario):
    eliminar_usuario(id_usuario)
    return success_response(message="Usuario desactivado correctamente")

@users_bp.route('/api/usuarios/<int:id_usuario>/force', methods=['DELETE'])
def delete_permanent(id_usuario):
    eliminar_usuario_fisico(id_usuario)
    return success_response(message="Usuario eliminado permanentemente de la BD")

@users_bp.route('/api/usuarios/<int:id_usuario>/toggle', methods=['PUT'])
def toggle_usuario(id_usuario):
    toggle_estado_usuario(id_usuario)
    return success_response(message="Estado del usuario actualizado")