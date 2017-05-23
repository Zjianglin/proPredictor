from datetime import datetime

from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request
from flask_login import login_required, current_user
from .response import response, error
from app import db, datasets
from app.main.tasks import build_estimator, update_chart
from . import main
from .forms import DatasetForm, SearchDataset, BuildModelForm
from .proM import dataset_info
from ..models import Dataset, Estimator, Topic
import os


@main.route('/datasets', methods=['GET', 'POST'])
@main.route('/datasets/<int:page>')
@login_required
def datasets_index(page=1):
    form = DatasetForm()
    if form.validate_on_submit():
        filename = datasets.save(form.dataset.data)
        new_dataset = Dataset(name=filename, user_id=current_user.id)
        db.session.add(new_dataset)
        flash('upload new dataset successfully', 'success')

    datas = Dataset.query \
                    .filter_by(user_id=current_user.id) \
                    .order_by(Dataset.timestamp.desc()) \
                    .paginate(page=page,
                              per_page=current_app.config['ITEMS_PER_PAGE'],
                              error_out=False)
    return render_template('datasets.html', form=form, datasets=datas)

@main.route('/dataset/del/<id>')
@login_required
def delete_dataset(id):
    data = Dataset.query.filter_by(id=id).first()
    if data is None or current_user.id != data.user_id:
        flash('Failed to delete dataset(id={})'.format(id), 'error')
    else:
        db.session.delete(data)
        db.session.commit()
        os.remove(os.path.join(
            current_app.config['UPLOADED_DATASETS_DEST'], data.name))
        flash('Succeed to delete dataset: {}'.format(data.name), 'info')
    return redirect(url_for('main.datasets_index'))

@main.route('/features', methods=['GET', 'POST'])
@login_required
def features_index():
    statistics = dict()
    session['analyse'] = False
    if request.method == 'POST':
        #print(request.form)
        dataset = Dataset.query.filter_by(id=request.form['id']).first()
        if dataset is None or dataset.user_id != current_user.id:
            flash('You have no dataset with id {}'.format(
                request.form['id']), 'error')
        else:
            path = current_app.config['UPLOADED_DATASETS_DEST'] + '/'\
                                    + dataset.name
            try:
                statistics = dataset_info(path)
                session['analyse'] = True
            except Exception as err:
                flash(err, 'error')

    return render_template('features.html',
                           statistics=statistics,
                           analyse=session.get('analyse', False))

@main.route('/models/build', methods=['POST'])
@login_required
def build_model():
    form = dict(request.get_json(force=True))

    target = form['target']
    features = form['features']
    name =   form['name']
    topic_id = form['topic_id']
    filepath = form['filepath']

    if not target:
        return error(400, "target is required")
    elif not features:
        return error(400, "features are required")
    else:
        clf = Estimator(name=name, features=features, target=target,
                        topic_id=topic_id, user_id=current_user.id)
        db.session.add(clf)
        build_estimator(clf=clf, filepath=filepath,
                              target=target, features=features)
        topic = Topic.query.filter_by(id=topic_id).first()
        update_chart(topic)
        return response(200, url_for('main.topic_index'))
