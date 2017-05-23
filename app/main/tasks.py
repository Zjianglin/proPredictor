from app import  db
from celery.utils.log import get_task_logger
import pandas as pd
from pickle import loads, dumps
from datetime import datetime
from app.main.proM import train_model
from flask import current_app
from app.models import Estimator
from app import create_celery_app
from app.task_queue import back_task
import json
import logging
import os
import matplotlib.pyplot as plt
import seaborn
import numpy as np

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


def update_chart(topic, filename=None):
    if topic.estimators is None:
        if topic.chart:
            os.remove(topic.chart)
            topic.chart = None
            topic.chart_clfs = 0
        return
    elif filename is None:
        filename = os.path.join(
            current_app.config['UPLOADED_CHARTS_DEST'],
            topic.name.replace(" ", "_") + '.png')
    print(filename)
    pers = dict()
    for estimator in topic.estimators:
        performance = json.loads(estimator.performance)
        for k, v in performance.items():
            if k == "performance":
                k = estimator.name + '_RFR'
            pers[k] = [float(p) for p in v.split('\t')]
            pers[k][2] *= 100
    #print(pers)
    seaborn.set()
    n = len(pers.keys())
    '''
    X = np.array([0, 1.1])
    fig = plt.figure(figsize=(12, 8))
    f, ax = plt.subplots(1, 2)
    labels = ['MAE', 'RMSE', 'MAPE']
    bar_width = float('%.2f' % ((1 - 0.2) / (n - 1)))
    print(bar_width)
    for i, k in enumerate(pers.keys()):
        XX = X + i * bar_width
        print(XX)
        ax[0].bar(XX, pers[k][:2], width=bar_width, label=k)
        for x, y in zip(XX, pers[k][:2]):
            ax[0].text(x, y + 0.05, '%.2f' % y, ha='center',
                       va='bottom', rotation=90)
        ax[1].bar(i * bar_width, pers[k][2], width=bar_width, label=k)
        ax[1].text(i * bar_width, pers[k][2] + 0.05, '%.2f%%' % (pers[k][2]),
                   ha='center', va='bottom', rotation=90)
    ax[0].set_xticks(X[:2] + bar_width * len(pers.keys()) / 2)
    ax[0].set_xticklabels(labels[:2])
    ax[0].set_yticks([])
    ax[0].legend()
    ax[1].set_xticks([bar_width * len(pers.keys()) / 2])
    ax[1].set_xticklabels([labels[2]])
    ax[1].yaxis.tick_right()
    ax[0].set_title("estimator performace compare")
    '''
    X = np.arange(3)
    fig = plt.figure(figsize=(12, 8))
    labels = ['MAE', 'RMSE', 'MAPE']
    bar_width = float('%.2f' % ((1 - 0.2) / n))
    for i, k in enumerate(pers.keys()):
        XX = X + i * bar_width
        plt.bar(XX, pers[k], width=bar_width, label=k)
        for x, y in zip(XX[:2], pers[k][:2]):
            plt.text(x, y + 0.05, '%.2f' % y, ha='center', va='bottom', rotation=90)
        plt.text(XX[2], pers[k][2] + 0.05, '%.2f%%' % (pers[k][2]),
                   ha='center', va='bottom', rotation=90)
    plt.xticks(X + bar_width * len(pers.keys()) / 2, labels)
    plt.yticks([])
    plt.legend(loc='best')
    plt.title("estimator performance compare")
    plt.savefig(filename)

    topic.chart = filename
    topic.chart_clfs = len(topic.estimators)
    db.session.commit()
