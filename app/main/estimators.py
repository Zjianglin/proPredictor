from ..models import Dataset, Estimator
from . import main
from .. import db, datasets
import pandas as pd
from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request, copy_current_request_context, jsonify
from flask_login import login_required, current_user

@main.route('/estimators')
@main.route('/estimators/<int:page>')
@login_required
def estimators_index(page=1):
    estimators = Estimator.query\
                    .filter_by(user_id=current_user.id)\
                    .order_by(Estimator.timestamp.desc())\
                    .paginate(page=page,
                      per_page=current_app.config['ITEMS_PER_PAGE'],
                      error_out=False)

    return render_template('estimators.html', estimators=estimators)

@main.route('/estimators/del/<int:id>')
@login_required
def estimators_delete(id):
    estimator = Estimator.query.filter_by(id=id).first()
    if estimator is None or estimator.user_id != current_user.id:
        flash('Failed to delete estimator.')
        return redirect(url_for('main.error_404'))

    db.session.delete(estimator)
    db.session.commit()
    flash('Delete estimator({}) successfully'.format(id))
    return redirect(url_for('main.estimators_index'))
