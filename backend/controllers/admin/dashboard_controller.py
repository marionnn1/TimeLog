from flask import Blueprint, jsonify
from services.admin.dashboard_service import obtener_estadisticas

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    stats = obtener_estadisticas()
    return jsonify({"status": "success", "data": stats}), 200