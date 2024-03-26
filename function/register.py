from flask import render_template, redirect, url_for, request, session, flash, Blueprint
from pymysql import IntegrityError
from db.db import User, db

register_bp = Blueprint('register', __name__)


@register_bp.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        stunum = request.form.get('stunum')
        user = request.form.get('name')
        password = request.form.get('pass')

        existing_user_stunum = User.query.filter_by(stunum=stunum).first()
        existing_user_name = User.query.filter_by(name=user).first()

        if existing_user_stunum:
            flash("该学号已注册用户", "error")
        elif not stunum or not user or not password:
            flash("学号、用户名或密码不能为空", "error")
        elif existing_user_name:
            flash("该用户名已被注册", "error")
        else:
            new_user = User(stunum=stunum, name=user, passwd=password)
            db.session.add(new_user)
            try:
                db.session.commit()
                session['user'] = user  # Store username in session
                return redirect(url_for('dashboard.dashboard_route'))
            except IntegrityError as e:
                db.session.rollback()
                flash("注册失败，请重试", "error")

    return render_template('attestation/register.html')
