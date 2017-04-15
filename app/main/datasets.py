from ..models import Dataset
from . import main
from .. import db, datasets
import os
from flask import render_template, flash, session, redirect, url_for
from .forms import DatasetForm, SearchDataset
from flask_login import login_required, current_user

@main.route('/datasets', methods=['GET', 'POST'])
@login_required
def datasets_index():
    form = DatasetForm()
    datas = [ {'name': 'test_dataset_1.csv', 'id': 1, 'timestamp': '2017-4-10'},
              {'name': 'test_dataset_2.csv', 'id': 2},
              {'name': 'test_dataset_3.csv', 'id': 3}]
    if form.validate_on_submit():
        filename = datasets.save(form.dataset.data)
        new_dataset = Dataset(name=filename, user_id=current_user.id)
        db.session.add(new_dataset)
        flash('upload new dataset successfully')
        datas.append(filename)

    return render_template('datasets.html', form=form, datasets=datas)

@main.route('/dataset/del/<id>')
@login_required
def delete_dataset(id):
    data = Dataset.query.filter_by(id=id).first()
    if data is None or current_user.id != data.user_id:
        flash('Failed to delete dataset: {}'.format(data.name), 'error')
    else:
        db.session.delete(data)
        db.session.commit()
        flash('Succeed to delete dataset: {}'.format(data.name), 'info')
    return redirect(url_for('main.datasets_index'))

@main.route('/features', methods=['GET', 'POST'])
@login_required
def features_index():
    search = SearchDataset()
    if search.validate_on_submit():
        dataset = Dataset.query.filter_by(id=search.dataset_id.data).first()
        if dataset is None or dataset.user_id != current_user.id:
            flash('You have no dataset with id {}'.format(
                    search.dataset_id.data), 'error')
        else:
            pass
    return render_template('features.html', form=search,
                           analyse=session.get('analyse', True))