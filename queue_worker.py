from app import create_app
from app.task_queue import queue_daemon
import os


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
queue_daemon(app)
