from flask import Blueprint, jsonify, request, g
from auth import require_auth
from services.manager.closing_service import get_closing_audit, toggle_closing_month
from errors import APIError

closing_bp = Blueprint('manager_closing', __name__, url_prefix='/api/manager/closing')

@closing_bp.route('', methods=['GET'], strict_slashes=False)
@require_auth
def get_closing():
    mes = request.args.get('mes')
    if not mes: raise APIError("Falta el parámetro 'mes'", status_code=400)

    data = get_closing_audit(mes)
    return jsonify({"status": "success", "data": data}), 200

@closing_bp.route('', methods=['POST'], strict_slashes=False)
@require_auth
def toggle_closing():
    body = request.get_json()
    mes = body.get('mes')
    accion = body.get('accion') 
    manager_id = g.usuario_actual.id 
    
    if not mes or not accion:
        raise APIError("Faltan parámetros 'mes' o 'accion'", status_code=400)

    toggle_closing_month(mes, accion, manager_id) 
    return jsonify({"status": "success", "message": f"Mes {accion} correctamente"}), 200