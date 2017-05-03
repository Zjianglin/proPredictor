from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import  DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from .. import datasets

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DatasetForm(FlaskForm):
    dataset = FileField(validators=[
        FileAllowed(datasets, 'Only csv format allowed'),
        FileRequired('Dataset required')
    ])
    submit = SubmitField('Upload')

class SearchDataset(FlaskForm):
    dataset_id = IntegerField('', validators=[DataRequired()], render_kw={
                            "placeholder": "Enter target dataset id"})
    submit = SubmitField('Search')

class BuildModelForm(FlaskForm):
    features = StringField('numerical features', id='features')
    submit = SubmitField('Build', id='build')