from flask import Blueprint, jsonify, request
from services.manager.closing_service import get_closing_audit, toggle_closing_month

closing_bp = Blueprint('manager_closing', __name__, url_prefix='/api/manager/closing')

@closing_bp.route('', methods=['GET'], strict_slashes=False)
def get_closing():
    month = request.args.get('month')
    if not month:
        return jsonify({"error": "Falta el parámetro 'month'"}), 400

    data, status = get_closing_audit(month)
    return jsonify(data), status

@closing_bp.route('', methods=['POST'], strict_slashes=False)
def toggle_closing():
    body = request.get_json()
    month = body.get('month')
    action = body.get('accion') 
    
    if not month or not action:
        return jsonify({"error": "Faltan parámetros 'month' o 'accion'"}), 400

    data, status = toggle_closing_month(month, action)
    return jsonify(data), status