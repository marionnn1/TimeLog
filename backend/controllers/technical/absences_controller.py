from flask import Blueprint, request, jsonify
from services.technical.absences_service import get_monthly_absences, save_absences, delete_absence
from datetime import datetime

absences_bp = Blueprint('absences', __name__)

@absences_bp.route('/api/absences', methods=['GET'])
def get_absences():
    try:
        month = int(request.args.get('month', datetime.now().month))
        year = int(request.args.get('year', datetime.now().year))
    except (ValueError, TypeError):
        month = datetime.now().month
        year = datetime.now().year
        
    data = get_monthly_absences(month, year)
    return jsonify({"status": "success", "data": data})

@absences_bp.route('/api/absences', methods=['POST'])
def create_absences():
    req_data = request.json
    if not req_data: return jsonify({"status": "error"}), 400
    
    success = save_absences(
        req_data.get('user_id'), 
        req_data.get('dates'), 
        req_data.get('type'), 
        req_data.get('comment', '')
    )
    return jsonify({"status": "success" if success else "error"}), 200 if success else 500

@absences_bp.route('/api/absences', methods=['DELETE'])
def remove_absence():
    req_data = request.json
    if not req_data: return jsonify({"status": "error"}), 400
    
    success = delete_absence(req_data.get('user_id'), req_data.get('date'))
    return jsonify({"status": "success" if success else "error"}), 200 if success else 500