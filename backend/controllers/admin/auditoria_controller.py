from flask import Blueprint, jsonify
from services.admin.auditoria_service import obtener_logs

auditoria_bp = Blueprint('auditoria', __name__)

@auditoria_bp.route('/api/auditoria', methods=['GET'])
def get_logs():
    logs = obtener_logs()
    if logs is not None:
        return jsonify({"status": "success", "data": logs}), 200
    return jsonify({"status": "error", "message": "Error al cargar la auditoría"}), 500