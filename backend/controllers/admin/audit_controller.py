from flask import Blueprint
from services.admin.audit_service import obtener_logs
from utils.responses import success_response # Usamos nuestra nueva utilidad

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/auditoria', methods=['GET'])
def get_logs():
    logs = obtener_logs()
    
    return success_response(
        data=logs, 
        message="Registros de auditoría cargados correctamente"
    )