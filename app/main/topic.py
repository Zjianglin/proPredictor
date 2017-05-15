from ..models import Topic, Estimator
from . import main
from .. import db, datasets
from .response import response, error
from flask import render_template, flash, session, redirect, url_for, current_app
from flask import request, copy_current_request_context, jsonify
from flask_login import login_required, current_user
import os
@main.route('/topic')
@main.route('/topic/<int:page>')
@login_required
def topic_index(page=1):
    topics = Topic.query \
                    .filter_by(user_id=current_user.id) \
                    .order_by(Topic.timestamp.desc()) \
                    .paginate(page=page,
                              per_page=current_app.config['ITEMS_PER_PAGE'],
                              error_out=False)
    return render_template('topics.html', topics=topics)

@main.route('/topic/ids')
@login_required
def topic_ids():
    topics = Topic.query.filter_by(user_id=current_user.id).all()
    result = []
    for t in topics:
        result.append((t.id, t.name))

    return response(200, result)

@main.route('/topic/add', methods=['POST'])
@login_required
def topic_insert():
    data = request.get_json()
    if not data or not data['name']:
        return error(400, "topic name can't be empty")
    topic = Topic(name=data.get('name'),
                  describe=data.get('describe'),
                  user_id=current_user.id)
    db.session.add(topic)
    db.session.commit()
    return response(200, topic.to_json())

@main.route(('/topic/del/<id>'), methods=['DELETE'])
@login_required
def topic_delete(id):
    topic = Topic.query\
                 .filter_by(id=id, user_id=current_user.id)\
                 .first_or_404()
    if topic.chart:
        os.remove(topic.chart)
    db.session.delete(topic)
    db.session.commit()
    return response(200, "delete  topic [{}] successfully".format(topic.name))
