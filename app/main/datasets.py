from datetime import datetime
from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request
from flask_login import login_required, current_user
from app import db, datasets
from app.tasks import build_estimator
from . import main
from .forms import DatasetForm, SearchDataset, BuildModelForm
from .proM import dataset_info
from ..models import Dataset, Estimator


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
        flash('Failed to delete dataset(id={})'.format(id), 'error')
    else:
        db.session.delete(data)
        db.session.commit()
        flash('Succeed to delete dataset: {}'.format(data.name), 'info')
    return redirect(url_for('main.datasets_index'))

@main.route('/features', methods=['GET', 'POST'])
@login_required
def features_index():
    search = SearchDataset()
    build_form = BuildModelForm()
    statistics = dict()
    session['analyse'] = False
    if search.validate_on_submit():
        dataset = Dataset.query.filter_by(id=search.dataset_id.data).first()
        if dataset is None or dataset.user_id != current_user.id:
            flash('You have no dataset with id {}'.format(
                    search.dataset_id.data), 'error')
        else:
            path = current_app.config['UPLOADED_DATASETS_DEST'] + '/'\
                                    + dataset.name
            try:
                statistics = dataset_info(path)
                session['analyse'] = True
            except Exception as err:
                flash(err, 'error')

    return render_template('features.html', form=search,
                           build_form=build_form,
                           statistics=statistics,
                           analyse=session.get('analyse', False))

@main.route('/models/build', methods=['POST'])
@login_required
def build_model():
    params = request.form
    features = [f.strip() for f in params.get('features')
                                            .strip().split(',')
                            if f.strip()]
    target = params.get('target', '').strip()
    name =   params.get('name', 'Estimator_{}'.format(
                            datetime.utcnow())).strip()
    filepath = params.get('filepath')
    if not target:
        flash('target is required', 'warning')
    elif not features:
        flash('features at least one required')
    else:
        clf = Estimator(name=name, features=features, target=target,
                        user_id=current_user.id)
        db.session.add(clf)
        db.session.commit()
        print('add new esitmator...')
        #build a model async
        build_estimator.delay(clf=clf, filepath=filepath,
                              target=target, features=features)
        flash('Building the model...', 'info')

    return redirect('/features')

