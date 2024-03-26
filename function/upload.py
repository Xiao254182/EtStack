import os

from flask import request, redirect, url_for, render_template
from werkzeug.utils import secure_filename


def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        upload_path = os.path.join(basepath, '/vm-iso', secure_filename(f.filename))
        f.save(upload_path)
        return redirect(url_for('dashboard'))
    return render_template('dashboard/dashboard.html')
