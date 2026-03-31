from flask import Blueprint, request, jsonify
from auth import require_auth
from services.admin.users_service import (
    toggle_estado_usuario,
    obtener_usuarios,
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario,
    eliminar_usuario_fisico,
    sincronizar_usuario,
)

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/usuarios", methods=["GET"])
@require_auth
def get_all():
    usuarios = obtener_usuarios()
    return jsonify({"status": "success", "data": usuarios}), 200


@users_bp.route("/api/usuarios", methods=["POST"])
@require_auth
def create():
    crear_usuario(request.json)
    return jsonify({"status": "success", "message": "Usuario creado"}), 201


@users_bp.route("/api/usuarios/<int:id_usuario>", methods=["PUT"])
@require_auth
def update(id_usuario):
    actualizar_usuario(id_usuario, request.json)
    return jsonify({"status": "success", "message": "Usuario actualizado"}), 200


@users_bp.route("/api/usuarios/<int:id_usuario>", methods=["DELETE"])
@require_auth
def deactivate(id_usuario):
    eliminar_usuario(id_usuario)
    return (
        jsonify({"status": "success", "message": "Usuario desactivado correctamente"}),
        200,
    )


@users_bp.route("/api/usuarios/<int:id_usuario>/force", methods=["DELETE"])
@require_auth
def delete_permanent(id_usuario):
    eliminar_usuario_fisico(id_usuario)
    return (
        jsonify(
            {
                "status": "success",
                "message": "Usuario eliminado permanentemente de la BD",
            }
        ),
        200,
    )


@users_bp.route("/api/usuarios/<int:id_usuario>/toggle", methods=["PUT"])
@require_auth
def toggle_usuario(id_usuario):
    toggle_estado_usuario(id_usuario)
    return (
        jsonify({"status": "success", "message": "Estado del usuario actualizado"}),
        200,
    )


@users_bp.route("/api/usuarios/sync", methods=["POST"])
def sync_user():
    datos = request.json
    user_data = sincronizar_usuario(datos)
    return jsonify({"status": "success", "data": user_data}), 200
