from flask import Blueprint, jsonify
from services.admin.dashboard_service import obtener_estadisticas
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    stats = obtener_estadisticas()
    if stats is not None:
        return jsonify({"status": "success", "data": stats}), 200
    return jsonify({"status": "error", "message": "Error al cargar estadísticas"}), 500