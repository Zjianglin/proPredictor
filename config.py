import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'This string is secret')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <zjianglin@foxmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    UPLOADED_DATASETS_DEST = os.path.join(basedir, 'app', 'static', 'datasets')
    UPLOADED_CHARTS_DEST = os.path.join(basedir, 'app', 'static', 'img')
    REDIS_QUEUE_KEY = 'PROCESS_DURATION_PREDICT'
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    CELERY_BACKEND_URL = 'redis://127.0.0.1:6379/0'
    ITEMS_PER_PAGE = 5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL',
             'mysql+pymysql://demo:test123@localhost:3306/demo')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL',
             'mysql+pymysql://demo:test123@localhost:3306/demo')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
             'mysql+pymysql://demo:test123@localhost:3306/demo')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}