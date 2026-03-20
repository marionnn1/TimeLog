from flask import Blueprint, jsonify, request
from services.manager.analytics_service import get_analytics_data

manager_analytics_bp = Blueprint('manager_analytics', __name__, url_prefix='/api/manager/analytics')

@manager_analytics_bp.route('', methods=['GET'], strict_slashes=False)
@manager_analytics_bp.route('/', methods=['GET'], strict_slashes=False)
def get_analytics():
    mes = request.args.get('mes')
    
    if not mes:
        return jsonify({"error": "Falta el parámetro 'mes'"}), 400

    data, status_code = get_analytics_data(mes)
    return jsonify(data), status_code