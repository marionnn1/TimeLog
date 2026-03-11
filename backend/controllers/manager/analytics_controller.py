from flask import Blueprint, jsonify, request
from services.manager.analytics_service import get_analytics_data

manager_analytics_bp = Blueprint('manager_analytics', __name__, url_prefix='/api/manager/analytics')

@manager_analytics_bp.route('/', methods=['GET'])
def get_analytics():
    month = request.args.get('month')
    
    if not month:
        return jsonify({"error": "Falta el parámetro 'month'"}), 400

    data, status_code = get_analytics_data(month)
    return jsonify(data), status_code