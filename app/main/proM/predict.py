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

def baseline(ydata):
    if not isinstance(ydata, pd.Series):
        ydata = pd.Series(ydata)

    base_pred = [ydata.mean()] * ydata.shape[0]
    base_rmse = np.sqrt(mean_squared_error(ydata, base_pred))
    base_mae = mean_absolute_error(ydata, base_pred)
    base_mape = np.average(np.abs(ydata - base_pred) / ydata)
    return '{:.3f}\t{:.3f}\t{:.3f}'.format(
                    base_mae, base_rmse, base_mape)

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
    performace = cross_validation(model=estimator, X=X, y=y, cv=5)
    performace = {
                'baseline': baseline(y),
                'performance': '{:.3f}\t{:.3f}\t{:.3f}'.format(
                    performace[0], performace[1], performace[2])
    }
    return (estimator,  json.dumps(performace))