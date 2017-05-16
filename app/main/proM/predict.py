import pandas as pd
import numpy as np
import io
from sklearn.pipeline import make_pipeline
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold, GridSearchCV
from sklearn import decomposition
from sklearn import metrics
import statistics
from stop_words import get_stop_words
from flask import json


def cross_validation(model, X, y, cv=3):
    """Return (MAE, RMSE, MAPE)"""
    kf = KFold(n_splits=cv)
    xval_err = 0
    abs_err = 0
    abs_per_err = 0
    for train_id, test_id in kf.split(X):
        X_train, y_train = X.iloc[train_id], y[train_id]
        X_test, y_test = X.iloc[test_id], y[test_id]
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        abs_err += mean_absolute_error(y_test, y_pred)
        abs_per_err += np.average(np.abs(y_test - y_pred) / y_test)
        xval_err += np.sqrt(mean_squared_error(y_test, y_pred))

        # print('LR.score(X_test, y_test):{}'.format(
        #     model.score(X_test, y_test)))
    return (abs_err / cv, xval_err / cv, abs_per_err / cv)

def average_total_flow(y, cv=10):
    if not isinstance(y, pd.Series):
        y = pd.Series(y)

    kf = KFold(n_splits=cv)
    xval_err = 0
    abs_err = 0
    abs_per_err = 0
    for train_id, test_id in kf.split(y):
        y_train = y[train_id]
        y_test = y[test_id]
        y_pred = [y_train.mean()] * y_test.shape[0]
        abs_err += mean_absolute_error(y_test, y_pred)
        abs_per_err += np.average(np.abs(y_test - y_pred) / y_test)
        xval_err += np.sqrt(mean_squared_error(y_test, y_pred))

    base_mae = abs_err / cv
    base_rmse = xval_err / cv
    base_mape = abs_per_err / cv

    return '{:.2f}\t{:.2f}\t{:.4f}'.format(
                    base_mae, base_rmse, base_mape)
def average_recent_10(y, cv=10):
    if not isinstance(y, pd.Series):
        y = pd.Series(y)

    kf = KFold(n_splits=cv)
    xval_err = 0
    abs_err = 0
    abs_per_err = 0
    for train_id, test_id in kf.split(y):
        y_train = y[train_id]
        y_test = y[test_id]
        k = 10 if y_train.shape[0] >= 10 else y_train.shape[0]
        y_pred = [y_train[-k:].mean()] * y_test.shape[0]
        abs_err += mean_absolute_error(y_test, y_pred)
        abs_per_err += np.average(np.abs(y_test - y_pred) / y_test)
        xval_err += np.sqrt(mean_squared_error(y_test, y_pred))

    base_mae = abs_err / cv
    base_rmse = xval_err / cv
    base_mape = abs_per_err / cv

    return '{:.2f}\t{:.2f}\t{:.4f}'.format(
        base_mae, base_rmse, base_mape)

def baseline(ydata):
    return {
        'average_total_flow': average_total_flow(ydata),
        'average_recent_10': average_recent_10(ydata)
    }

def best_RFR(xdata, target, search=False, verbose=False):
    '''using grid search to find the optimal RandomForestRegressor model'''
    if search:
        param_grid = {
                'n_estimators': range(5, 25, 5),
                'max_features': ('auto', 'sqrt', 'log2'),
                'warm_start': (True, ),
                }
        grid = GridSearchCV(RandomForestRegressor(), param_grid, n_jobs=-1)
        grid.fit(xdata, target)

        best_params_ =  grid.best_params_
    else:
        best_params_ = {'max_features': 'auto', 'n_estimators': 20,
                        'n_jobs': -1, 'oob_score': True,
                        'random_state': 31}
    if verbose:
        print('----RFR best params----')
        print(best_params_)
        print('-' * 40)
    return RandomForestRegressor(**best_params_)

def train_model(X, y):
    estimator = best_RFR(X, y)
    performance = cross_validation(model=estimator, X=X, y=y, cv=5)
    performance = dict(performance='{:.2f}\t{:.2f}\t{:.4f}'.format(
                    performance[0], performance[1], performance[2]))
    performance.update(baseline(y))
    return (estimator,  json.dumps(performance))