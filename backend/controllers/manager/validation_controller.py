from flask import Blueprint, jsonify, request, g
from auth import require_auth
from services.manager.validation_service import get_pending_validations, approve_validation, reject_validation
from errors import APIError

validation_bp = Blueprint('manager_validation', __name__, url_prefix='/api/manager/validation')

@validation_bp.route('', methods=['GET'], strict_slashes=False)
@validation_bp.route('/', methods=['GET'], strict_slashes=False)
@require_auth
def get_validations():
    data = get_pending_validations()
    return jsonify({"status": "success", "data": data}), 200

@validation_bp.route('/<int:id>/approve', methods=['PUT'], strict_slashes=False)
@require_auth
def approve(id):
    body = request.get_json()
    horas = body.get('horas')
    manager_id = g.usuario_actual.id 
    
    if horas is None: raise APIError("Faltan las horas corregidas", status_code=400)
    
    approve_validation(id, horas, manager_id) 
    return jsonify({"status": "success", "message": "Solicitud aprobada"}), 200

@validation_bp.route('/<int:id>/reject', methods=['PUT'], strict_slashes=False)
@require_auth
def reject(id):
    body = request.get_json()
    motivo = body.get('motivo')
    manager_id = g.usuario_actual.id 
    
    if not motivo: raise APIError("Falta el motivo de rechazo", status_code=400)
        
    reject_validation(id, motivo, manager_id) 
    return jsonify({"status": "success", "message": "Solicitud rechazada"}), 200