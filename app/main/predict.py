from ..models import Dataset, Estimator
from . import main
from .. import db, datasets
from pandas import Series
from .response import error, response
from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request, copy_current_request_context, jsonify
from .forms import DatasetForm, SearchDataset, BuildModelForm
from .proM import dataset_info, train_model
from pickle import loads
from flask_login import login_required, current_user

@main.route('/predict/<int:id>')
@login_required
def predict_index(id):
    estimator = Estimator.query.filter_by(id=id, status=1).first_or_404()
    params = {
        'id': id,
        'target': estimator.target,
        'features': estimator.features
    }

    return render_template('predict.html', params=params)

@main.route('/predict', methods=['POST'])
@login_required
def predict_active():
    params = request.form
    if '' in params.values():
        return error(400, 'features must be filled totally.')
    estimator = Estimator.query.filter_by(id=params.get('id'),
                                          status=1).first_or_404();
    xdata = Series([params.get(k) for k in estimator.features],
                    index=estimator.features)
    estimator = loads(estimator.estimator)
    #print(estimator)
    target = estimator.predict(xdata.values.reshape(1, -1))[0]
    target = '{:.3f}'.format(target)
    print(target)

    return response(200, target)