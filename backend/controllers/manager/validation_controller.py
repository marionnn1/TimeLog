from flask import Blueprint, jsonify, request
from services.manager.validation_service import get_pending_validations, approve_validation, reject_validation

validation_bp = Blueprint('manager_validation', __name__, url_prefix='/api/manager/validation')

@validation_bp.route('', methods=['GET'], strict_slashes=False)
@validation_bp.route('/', methods=['GET'], strict_slashes=False)
def get_validations():
    data, status = get_pending_validations()
    return jsonify(data), status

@validation_bp.route('/<int:id>/approve', methods=['PUT'], strict_slashes=False)
def approve(id):
    body = request.get_json()
    horas = body.get('horas')
    manager_id = body.get('manager_id') 
    
    if horas is None:
        return jsonify({"error": "Faltan las horas corregidas"}), 400
    
    data, status = approve_validation(id, horas, manager_id) 
    return jsonify(data), status

@validation_bp.route('/<int:id>/reject', methods=['PUT'], strict_slashes=False)
def reject(id):
    body = request.get_json()
    motivo = body.get('motivo')
    manager_id = body.get('manager_id') 
    
    if not motivo:
        return jsonify({"error": "Falta el motivo de rechazo"}), 400
        
    data, status = reject_validation(id, motivo, manager_id) 
    return jsonify(data), status