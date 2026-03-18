from flask import Blueprint, jsonify, request
from services.manager.closing_service import get_closing_audit, toggle_closing_month

closing_bp = Blueprint('manager_closing', __name__, url_prefix='/api/manager/closing')

@closing_bp.route('', methods=['GET'], strict_slashes=False)
def get_closing():
    mes = request.args.get('mes')
    if not mes:
        return jsonify({"error": "Falta el parámetro 'mes'"}), 400

    data, status = get_closing_audit(mes)
    return jsonify(data), status

@closing_bp.route('', methods=['POST'], strict_slashes=False)
def toggle_closing():
    body = request.get_json()
    mes = body.get('mes')
    accion = body.get('accion') # 'cerrar' o 'reabrir'
    
    if not mes or not accion:
        return jsonify({"error": "Faltan parámetros 'mes' o 'accion'"}), 400

    data, status = toggle_closing_month(mes, accion)
    return jsonify(data), status