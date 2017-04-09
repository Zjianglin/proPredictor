from ..models import Dataset
from . import main
from .. import db, datasets
import os
from flask import render_template, request, current_app
from .forms import DatasetForm
from flask_login import login_required

@main.route('/datasets', methods=['GET', 'POST'])
@login_required
def datasets_index():
    form = DatasetForm()
    datas = ['test 1', 'test 2']
    if form.validate_on_submit():
        filename = datasets.save(form.dataset.data)
        new_dataset = Dataset(name=filename)
        db.session.add(new_dataset)
        datas.append(filename)

    return render_template('datasets.html', form=form, datasets=datas)
