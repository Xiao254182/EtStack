from flask import render_template, redirect, url_for, request, session, flash, Blueprint
from db.db import User

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        user_name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(name=user_name).first()

        if not user:
            flash("用户不存在，请先注册", "error")
        elif user.passwd != password:
            flash("密码不正确", "error")
        else:
            session['user'] = user_name
            return redirect(url_for('dashboard.dashboard_route'))

    return render_template('attestation/login.html')
