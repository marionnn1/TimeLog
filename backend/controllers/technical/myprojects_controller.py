from flask import Blueprint, request, jsonify
from TimeLog.backend.services.technical.myprojects_service import (
    request_time_entry_correction,
    get_weekly_time_entries, 
    save_time_entries_batch, 
    get_monthly_analytics,
    get_team_analytics,
    get_monthly_calendar
)
from datetime import datetime

myprojects_bp = Blueprint('myprojects', __name__)

@myprojects_bp.route('/api/myprojects/week', methods=['GET'])
def get_week():
    user_id = request.args.get('user_id')
    monday_date = request.args.get('monday_date')
    return jsonify({"status": "success", "data": get_weekly_time_entries(user_id, monday_date)})

@myprojects_bp.route('/api/myprojects/monthly-analytic', methods=['GET'])
def get_analytics():
    user_id = request.args.get('user_id')
    try:
        month = int(request.args.get('month', datetime.now().month))
        year = int(request.args.get('year', datetime.now().year))
    except (ValueError, TypeError):
        month, year = datetime.now().month, datetime.now().year

    data = get_monthly_analytics(user_id, month, year)
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/team-analytic', methods=['GET'])
def get_team_stats():
    try:
        month = int(request.args.get('month', datetime.now().month))
        year = int(request.args.get('year', datetime.now().year))
    except (ValueError, TypeError):
        month, year = datetime.now().month, datetime.now().year

    data = get_team_analytics(month, year)
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/save', methods=['POST'])
def save():
    req_data = request.json
    if not req_data: return jsonify({"status": "error"}), 400
    
    success = save_time_entries_batch(
        req_data.get('user_id'), 
        req_data.get('rows'), 
        req_data.get('dates')
    )
    return jsonify({"status": "success" if success else "error"}), 200 if success else 500

@myprojects_bp.route('/api/myprojects/calendar', methods=['GET'])
def get_calendar():
    user_id = request.args.get('user_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    if not all([user_id, month, year]):
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
        
    data = get_monthly_calendar(user_id, int(month), int(year))
    return jsonify({"status": "success", "data": data})

@myprojects_bp.route('/api/myprojects/request-correction', methods=['POST'])
def request_correction():
    data = request.json
    if not data: 
        return jsonify({"status": "error", "message": "Empty data"}), 400

    user_id = data.get('user_id')
    project_id = data.get('project_id')
    date = data.get('date')
    new_hours = data.get('new_hours')
    reason = data.get('reason')

    if not all([user_id, project_id, date, new_hours is not None, reason]):
        return jsonify({"status": "error", "message": "Missing mandatory data"}), 400

    success = request_time_entry_correction(user_id, project_id, date, new_hours, reason)

    if success:
        return jsonify({"status": "success", "message": "Request sent to the manager"}), 200
    return jsonify({"status": "error", "message": "Failed to send request"}), 500