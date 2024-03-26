from flask import redirect, url_for, Blueprint

reload_bp = Blueprint('reload', __name__)


@reload_bp.route('/')
def reload_route():
    return redirect(url_for('login.login_route'))
