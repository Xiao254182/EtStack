import os
import subprocess

from flask import session, request, render_template, redirect, url_for, Blueprint, flash
from werkzeug.utils import secure_filename
from db.db import Host, db
from function.ttyd import start_ttyd  # 导入 start_ttyd 函数

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard_route():
    froms = request.form
    if "ttyd" in froms:
        if request.method == 'POST':
            ttyd_name = froms["ttyd"]
            start_ttyd(ttyd_name)
            return redirect('http://192.168.100.144:7681')
    if 'user' in session:
        if request.method == 'GET':
            user = session['user']
            hosts = Host.query.filter_by(user=user).all()
            return render_template('dashboard/dashboard.html', user=user, hosts=hosts)
        elif request.method == 'POST':
            # 文件上传处理
            try:
                os.makedirs('/vm-iso')
            except FileExistsError:
                pass

            f = request.files['file']
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath, '/vm-iso', secure_filename(f.filename))
            f.save(upload_path)

            user = session['user']
            hostname = request.form.get('hostname')

            existing_host = Host.query.filter_by(user=user, hostname=hostname).first()
            if existing_host:
                flash("该用户下已存在此虚拟机，请重新创建新的虚拟机", "error")
                return redirect(url_for('dashboard.dashboard_route'))

            image = f.filename
            cpu_count = request.form.get('cpu_count')
            memory_size = request.form.get('memory_size')
            disk_size = request.form.get('disk_size')
            new_host = Host(user=user, hostname=hostname, image=image, cpu_count=cpu_count,
                            memory_size=memory_size, disk_size=disk_size)

            db.session.add(new_host)
            db.session.commit()

            try:
                os.makedirs(f'/vm-disk-{user}')
            except FileExistsError:
                pass

            os.chdir(f'/vm-disk-{user}')

            subprocess.run(['qemu-img', 'create', '-f', 'raw', f'{hostname}.raw', f'{disk_size}G'])
            subprocess.run(['virt-install', '--name', hostname,
                            '--vcpus', cpu_count,
                            '--ram', memory_size,
                            '--location=/vm-iso/' + image,
                            '--disk', f'path=/vm-disk-{user}/{hostname}.raw,size={disk_size},format=raw',
                            '--network', 'bridge=br0', '--os-variant=rhel7.1',
                            '--extra-args=console=ttyS0',
                            '--noautoconsole',
                            '--force'])

            # 启动 ttyd 会话
            start_ttyd(hostname)

            return redirect(url_for('dashboard.dashboard_route'))
    else:
        return redirect(url_for('login.login_route'))
