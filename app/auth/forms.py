from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in', )

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
                        DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
                        DataRequired(), Length(1, 64),
                        Regexp('^[A-Za-z][\w.]*$', 0,'username must have'
                        'only letters, numbers, dots and underscore')])
    password = PasswordField('Password', validators=[
                        DataRequired(), Length(6, 16),
                        EqualTo('password2', message='Password must mathc.')])
    password2 = PasswordField('Password confirm', validators=[DataRequired()])
    submit = SubmitField('Sign up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has already exist')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has already exist')