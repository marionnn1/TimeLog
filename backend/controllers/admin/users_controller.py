from flask import Blueprint, request, jsonify
from services.admin.users_service import toggle_estado_usuario
from services.admin.users_service import (
    obtener_usuarios, 
    crear_usuario, 
    actualizar_usuario, 
    eliminar_usuario # Este ahora actúa como baja lógica (desactivar)
)

# Creamos el "molde" de rutas para usuarios
users_bp = Blueprint('users', __name__)

@users_bp.route('/api/usuarios', methods=['GET'])
def get_all():
    usuarios = obtener_usuarios()
    if usuarios is not None:
        return jsonify({"status": "success", "data": usuarios}), 200
    return jsonify({"status": "error", "message": "Error al conectar con la BD"}), 500

@users_bp.route('/api/usuarios', methods=['POST'])
def create():
    if crear_usuario(request.json):
        return jsonify({"status": "success", "message": "Usuario creado"}), 201
    return jsonify({"status": "error", "message": "Fallo al crear"}), 500

@users_bp.route('/api/usuarios/<int:id_usuario>', methods=['PUT'])
def update(id_usuario):
    if actualizar_usuario(id_usuario, request.json):
        return jsonify({"status": "success", "message": "Usuario actualizado"}), 200
    return jsonify({"status": "error", "message": "Fallo al actualizar"}), 500

# Ruta para la Baja Lógica (Desactivar usuario)
@users_bp.route('/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def deactivate(id_usuario):
    if eliminar_usuario(id_usuario):
        return jsonify({"status": "success", "message": "Usuario desactivado correctamente"}), 200
    return jsonify({"status": "error", "message": "Fallo al desactivar usuario"}), 500

# NUEVA: Ruta para el Borrado Físico (Eliminar de la BD definitivamente)
@users_bp.route('/api/usuarios/<int:id_usuario>/force', methods=['DELETE'])
def delete_permanent(id_usuario):
    # Nota: Asegúrate de tener esta función 'eliminar_usuario_fisico' en tu usuarios_service.py
    from services.admin.users_service import eliminar_usuario_fisico
    if eliminar_usuario_fisico(id_usuario):
        return jsonify({"status": "success", "message": "Usuario eliminado permanentemente de la BD"}), 200
    return jsonify({
        "status": "error", 
        "message": "No se puede eliminar de la BD: el usuario tiene datos vinculados (imputaciones o proyectos)"
    }), 500

@users_bp.route('/api/usuarios/<int:id_usuario>/toggle', methods=['PUT'])
def toggle_usuario(id_usuario):
    from services.admin.users_service import toggle_estado_usuario # Importar arriba
    exito = toggle_estado_usuario(id_usuario)
    if exito:
        return jsonify({"status": "success", "message": "Estado del usuario actualizado"}), 200
    return jsonify({"status": "error", "message": "No se pudo cambiar el estado"}), 500