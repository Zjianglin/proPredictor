from datetime import datetime
from flask import render_template, session, redirect, url_for
from flask_login import login_required
from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')
'''
@main.route('/datasets')
@login_required
def datasets():
    return render_template('datasets.html')
'''

@main.errorhandler(404)
@login_required
def error_404(e):
    return render_template('404.html'), 404

@main.errorhandler(500)
@login_required
def error_500(e):
    return render_template('500.html'), 500