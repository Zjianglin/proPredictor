from . import  db,celery
from celery.utils.log import get_task_logger
import pandas as pd
from pickle import loads, dumps
from datetime import datetime
from .main.proM import train_model
from .models import Estimator
from . import create_celery_app

logger = get_task_logger(__name__)

#celery = create_celery_app()

@celery.task
def build_estimator(clf, filepath, features, target):
    dataset = pd.read_csv(filepath)
    X = dataset[features]
    y = dataset[target]
    X.info() #debug
    clf = Estimator.query.filter_by(id=clf.id).first()
    print('build_estimator...')
    try:
        logger.info('train new esitmator...')
        # usually cost a lot of time
        model, performance = train_model(X, y)
    except:
        if clf:
            db.session.delete(clf)
    else:
        if clf:
            clf.status = 1
            clf.performance = performance
            clf.estimator = dumps(model)
            clf.timestamp = datetime.utcnow()
            db.session.update(clf)
            logger.info('update estimator...')
    db.session.commit()
    logger.info('finish train new estimator...')


@celery.task()
def test_add(x, y):
    print('test_add ...')
    return x * y