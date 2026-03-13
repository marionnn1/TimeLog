from flask import Blueprint, jsonify
from services.admin.audit_service import get_logs as obtener_logs

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/admin/audit', methods=['GET'])
def get_logs():
    logs = obtener_logs()
    if logs is not None:
        return jsonify({"status": "success", "data": logs}), 200
    return jsonify({"status": "error", "message": "Error al cargar la auditoría"}), 500