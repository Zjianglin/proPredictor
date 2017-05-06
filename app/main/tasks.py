from app import  db
from celery.utils.log import get_task_logger
import pandas as pd
from pickle import loads, dumps
from datetime import datetime
from app.main.proM import train_model
from app.models import Estimator
from app import create_celery_app
from app.task_queue import back_task
import logging

#celery = create_celery_app()
logger = logging.getLogger('tasks')

#@back_task
def build_estimator(clf, filepath, features, target):
    dataset = pd.read_csv(filepath)
    X = dataset[features]
    y = dataset[target]
    if clf is None:
        return
    try:
        # usually cost a lot of time
        model, performance = train_model(X, y)
    except Exception as err:
        if clf:
            db.session.delete(clf)
    else:
        if clf:
            clf.status = 1
            clf.performance = performance
            clf.estimator = dumps(model)
            clf.timestamp = datetime.now()
    db.session.commit()