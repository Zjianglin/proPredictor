from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True, index=True)
    password = db.column(db.String(16))

    def __repr__(self):
        return '<User {}>'.format(self.username)