from ..models import Dataset, Estimator
from . import main
from .. import db, datasets
import pandas as pd
from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request, copy_current_request_context, jsonify
from .forms import DatasetForm, SearchDataset, BuildModelForm
from .proM import dataset_info, train_model
from flask_login import login_required, current_user

@main.route('/predict/<int:id>', methods=['GET', 'POST'])
@login_required
def predict_index(id):
    flash('predict')
    return render_template('predict.html')