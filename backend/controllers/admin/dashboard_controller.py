from flask import Blueprint
from services.admin.dashboard_service import obtener_estadisticas
from utils.responses import success_response

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    stats = obtener_estadisticas()
    return success_response(data=stats, message="Estadísticas cargadas correctamente")