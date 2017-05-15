from ..models import Dataset, Estimator, Topic
from . import main
from .. import db, datasets
from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request, copy_current_request_context, jsonify
from flask_login import login_required, current_user
from .tasks import update_chart

@main.route('/estimators/del/<int:id>')
@login_required
def estimators_delete(id):
    estimator = Estimator.query.filter_by(id=id).first_or_404()
    if estimator is None or estimator.user_id != current_user.id:
        flash('Failed to delete estimator.')
        return redirect(url_for('main.error_404'))
    db.session.delete(estimator)

    topic = Topic.query.filter_by(id=estimator.topic_id).first()
    if topic:
        update_chart(topic)
    db.session.commit()
    flash('Delete estimator({}) successfully'.format(id))
    return redirect(url_for('main.topic_index'))
