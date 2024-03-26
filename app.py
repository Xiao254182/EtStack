from flask import Flask
from function.login import login_bp
from function.register import register_bp
from function.dashboard import dashboard_bp
from function.reload import reload_bp
from db.db import init_db

app = Flask(__name__)
app.secret_key = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:000000@localhost:3306/EtStack'

init_db(app)

app.register_blueprint(reload_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(register_bp)

if __name__ == '__main__':
    app.run()
