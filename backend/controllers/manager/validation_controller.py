from flask import Blueprint, request
from services.manager.validation_service import get_pending_validations, approve_validation, reject_validation
from utils.responses import success_response
from utils.exceptions import APIError

validation_bp = Blueprint('manager_validation', __name__, url_prefix='/api/manager/validation')

@validation_bp.route('', methods=['GET'], strict_slashes=False)
@validation_bp.route('/', methods=['GET'], strict_slashes=False)
def get_validations():
    return success_response(data=get_pending_validations())

@validation_bp.route('/<int:id>/approve', methods=['PUT'], strict_slashes=False)
def approve(id):
    body = request.get_json()
    horas = body.get('horas')
    if horas is None:
        raise APIError("Faltan las horas corregidas", 400)
    
    approve_validation(id, horas)
    return success_response(message="Solicitud aprobada")

@validation_bp.route('/<int:id>/reject', methods=['PUT'], strict_slashes=False)
def reject(id):
    body = request.get_json()
    motivo = body.get('motivo')
    if not motivo:
        raise APIError("Falta el motivo de rechazo", 400)
        
    reject_validation(id, motivo)
    return success_response(message="Solicitud rechazada")