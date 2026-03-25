from flask import Blueprint, request
from services.manager.validation_service import get_pending_validations, approve_validation, reject_validation
from utils.responses import success_response

tickets_bp = Blueprint('admin_tickets', __name__, url_prefix='/api/admin/tickets')

@tickets_bp.route('/', methods=['GET'])
def get_tickets():
    return success_response(data=get_pending_validations())

@tickets_bp.route('/<int:id>/approve', methods=['PUT'])
def approve(id):
    approve_validation(id, request.get_json().get('horas'))
    return success_response(message="Ticket aprobado y corregido")

@tickets_bp.route('/<int:id>/reject', methods=['PUT'])
def reject(id):
    reject_validation(id, request.get_json().get('motivo'))
    return success_response(message="Ticket rechazado")