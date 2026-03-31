from flask import Blueprint, jsonify, request, g
from auth import require_auth
from services.manager.analytics_service import get_analytics_data
from errors import APIError

manager_analytics_bp = Blueprint('manager_analytics', __name__, url_prefix='/api/manager/analytics')

@manager_analytics_bp.route('', methods=['GET'], strict_slashes=False)
@manager_analytics_bp.route('/', methods=['GET'], strict_slashes=False)
@require_auth
def get_analytics():
    mes = request.args.get('mes')
    if not mes:
        raise APIError("Falta el parámetro 'mes'", status_code=400)

    data = get_analytics_data(mes)
    return jsonify({"status": "success", "data": data}), 200