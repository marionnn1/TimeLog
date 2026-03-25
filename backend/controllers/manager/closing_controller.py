from flask import Blueprint, request
from services.manager.closing_service import get_closing_audit, toggle_closing_month
from utils.responses import success_response
from utils.exceptions import APIError

closing_bp = Blueprint('manager_closing', __name__, url_prefix='/api/manager/closing')

@closing_bp.route('', methods=['GET'], strict_slashes=False)
@closing_bp.route('/', methods=['GET'], strict_slashes=False)
def get_closing():
    mes = request.args.get('mes')
    if not mes:
        raise APIError("Falta el parámetro 'mes'", 400)
    return success_response(data=get_closing_audit(mes))

@closing_bp.route('', methods=['POST'], strict_slashes=False)
@closing_bp.route('/', methods=['POST'], strict_slashes=False)
def toggle_closing():
    body = request.get_json()
    mes = body.get('mes')
    accion = body.get('accion')
    if not mes or not accion:
        raise APIError("Faltan parámetros", 400)
    
    toggle_closing_month(mes, accion)
    return success_response(message=f"Mes {accion} correctamente")