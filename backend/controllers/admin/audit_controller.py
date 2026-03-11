from flask import Blueprint, jsonify
from TimeLog.backend.services.admin.audit_service import obtener_logs

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/audit', methods=['GET'])
def get_logs():
    logs = obtener_logs()
    if logs is not None:
        return jsonify({"status": "success", "data": logs}), 200
    return jsonify({"status": "error", "message": "Error al cargar la auditoría"}), 500