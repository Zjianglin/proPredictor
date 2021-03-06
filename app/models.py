from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
import os

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean(), default=False)
    topics = db.relationship('Topic', backref='user')
    datasets = db.relationship('Dataset', backref='user')

    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.password_hash)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, passwd):
        return check_password_hash(self.password_hash, passwd)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Dataset(db.Model):
    __tablename__ = 'datasets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<{}: {}>'.format(self.id, self.name)

    def get_dataset(self):
        return os.path.join(current_app.config['UPLOADED_DATASETS_DEST'],
                            self.name)

class Estimator(db.Model):
    __tablename__ = 'estimators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    estimator = db.Column(db.LargeBinary(65536), nullable=True)
    performance = db.Column(db.Text, default='')
    status = db.Column(db.Boolean, default=False)
    features_str = db.Column(db.Text, nullable=True)
    target = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Estimator {}: {}'.format(self.features,
                                             self.target)

    @property
    def features(self):
        if self.features_str is not None:
            return self.features_str.split('+')
        else:
            return []

    @features.setter
    def features(self, n_features=list([])):
        self.features_str = '+'.join(n_features)

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    describe = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    estimators = db.relationship('Estimator', cascade='all,delete', backref='topic')
    chart = db.Column(db.String(1024), unique=True)   #performace compare chart src
    chart_clfs = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'describe': self.describe
        }

    def chart_is_lastest(self):
        return len(self.estimators) == self.chart_clfs