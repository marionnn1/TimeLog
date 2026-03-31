from flask import Blueprint, jsonify
from auth import require_auth
from services.admin.audit_service import obtener_logs

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/auditoria', methods=['GET'])
@require_auth
def get_logs():
    logs = obtener_logs()
    return jsonify({"status": "success", "data": logs}), 200