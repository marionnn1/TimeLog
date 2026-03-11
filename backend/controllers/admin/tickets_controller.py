from flask import Blueprint, request, jsonify
# Reutilizamos los servicios de validación del manager
from services.manager.validation_service import get_pending_validations, approve_validation, reject_validation

tickets_bp = Blueprint('admin_tickets', __name__, url_prefix='/api/admin/tickets')

@tickets_bp.route('/', methods=['GET'])
def get_tickets():
    data, status = get_pending_validations()
    return jsonify(data), status

@tickets_bp.route('/<int:id>/approve', methods=['PUT'])
def approve(id):
    body = request.get_json()
    data, status = approve_validation(id, body.get('horas'))
    return jsonify(data), status

@tickets_bp.route('/<int:id>/reject', methods=['PUT'])
def reject(id):
    body = request.get_json()
    data, status = reject_validation(id, body.get('motivo'))
    return jsonify(data), status