from flask import Blueprint, request
from services.manager.analytics_service import get_analytics_data
from utils.responses import success_response
from utils.exceptions import APIError

manager_analytics_bp = Blueprint('manager_analytics', __name__, url_prefix='/api/manager/analytics')

@manager_analytics_bp.route('', methods=['GET'], strict_slashes=False)
@manager_analytics_bp.route('/', methods=['GET'], strict_slashes=False)
def get_analytics():
    mes = request.args.get('mes')
    if not mes:
        raise APIError("Falta el parámetro 'mes'", 400)

    data = get_analytics_data(mes)
    return success_response(data=data)