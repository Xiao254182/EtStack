from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    stunum = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(16), unique=True)
    passwd = db.Column(db.String(32))

    def __repr__(self):
        return '<User: %s %s %s %s>' % (self.id, self.stunum, self.name, self.passwd)


class Host(db.Model):
    __tablename__ = 'host'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(16))
    hostname = db.Column(db.String(100))
    image = db.Column(db.String(100))
    cpu_count = db.Column(db.Integer)
    memory_size = db.Column(db.Integer)
    disk_size = db.Column(db.Integer)

    def __repr__(self):
        return '<Host: %s %s %s %s %s %s %s>' % (
            self.id, self.user, self.hostname, self.image, self.cpu_count, self.memory_size, self.disk_size)


def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
