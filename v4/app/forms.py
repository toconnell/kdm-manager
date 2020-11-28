"""

    Flask forms are used by the Flask app, and not by the Angular app, which
    should be doing everything (or as much as it can) on the page without
    reloading.

"""

import flask_wtf
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    validators
)


class LoginForm(flask_wtf.FlaskForm):
    """ Super basic; used to authenticate into the app. """
    username = StringField('Email', validators=[
        validators.DataRequired(),
        validators.Email(),
        validators.Optional(strip_whitespace=True),
    ])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class ResetForm(flask_wtf.FlaskForm):
    """ Similar to the new user registration form; requires PW twice, etc. """

    username = StringField('Email', validators=[
        validators.DataRequired(),
        validators.Email(),
        validators.Optional(strip_whitespace=True)
    ])

    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match!')
    ])
    confirm = PasswordField('Password Again')

    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Reset password')
