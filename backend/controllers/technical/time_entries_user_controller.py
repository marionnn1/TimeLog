from flask import Blueprint, request, jsonify
# Añadimos _service para que coincida con el nombre de tu archivo
from services.technical.time_entries_user_service import get_weekly_time_entries, save_time_entries_batch

time_entries_user_bp = Blueprint('time_entries_user', __name__)

@time_entries_user_bp.route('/api/time-entries/week', methods=['GET'])
def get_week():
    user_id = request.args.get('user_id')
    monday_date = request.args.get('monday_date')
    
    if not user_id or not monday_date:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
    res = get_weekly_time_entries(user_id, monday_date)
    if res is not None:
        return jsonify({"status": "success", "data": res}), 200
    return jsonify({"status": "error", "message": "Error querying the DB"}), 500

@time_entries_user_bp.route('/api/time-entries/save', methods=['POST'])
def save_batch():
    data = request.json
    success = save_time_entries_batch(data['user_id'], data['rows'], data['dates'])
    if success:
        return jsonify({"status": "success", "message": "Time entries saved"}), 200
    return jsonify({"status": "error", "message": "Failed to save"}), 500