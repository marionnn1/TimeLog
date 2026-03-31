from flask import Blueprint, request, jsonify
from auth import require_auth
from services.manager.validation_service import (
    get_pending_validations,
    approve_validation,
    reject_validation,
)
from errors import APIError

tickets_bp = Blueprint("admin_tickets", __name__, url_prefix="/api/admin/tickets")


@tickets_bp.route("/", methods=["GET"])
@require_auth
def get_tickets():
    data = get_pending_validations()
    return jsonify({"status": "success", "data": data}), 200


@tickets_bp.route("/<int:id>/approve", methods=["PUT"])
@require_auth
def approve(id):
    body = request.get_json()
    if "horas" not in body:
        raise APIError("Faltan las horas", status_code=400)

    approve_validation(id, body.get("horas"))
    return jsonify({"status": "success", "message": "Ticket aprobado"}), 200


@tickets_bp.route("/<int:id>/reject", methods=["PUT"])
@require_auth
def reject(id):
    body = request.get_json()
    if not body.get("motivo"):
        raise APIError("Falta el motivo de rechazo", status_code=400)

    reject_validation(id, body.get("motivo"))
    return jsonify({"status": "success", "message": "Ticket rechazado"}), 200
