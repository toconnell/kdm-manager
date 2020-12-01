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


#
#   re-usable constants for forms
#

USERNAME = StringField(
    'Email',
        validators = [
            validators.DataRequired(),
            validators.Email(),
            validators.Optional(strip_whitespace=True)
        ]
    )
PASSWORD = PasswordField(
    'Password',
    validators = [validators.DataRequired()]
)
REMEMBER = BooleanField('Remember Me')


class LoginForm(flask_wtf.FlaskForm):
    """ Super basic; used to authenticate into the app. """
    username = USERNAME
    password = PASSWORD
    remember_me = REMEMBER
    submit = SubmitField('Sign in')


class RegisterForm(flask_wtf.FlaskForm):
    """ Similar to LoginForm, but with a password confimration. """

    username = USERNAME

    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match!')
    ])
    confirm = PasswordField('Password (again)')

    submit = SubmitField('Register')


class ResetForm(flask_wtf.FlaskForm):
    """ Asks for the password twice, but otherwise is the same as the regular
    sign-in form. """

    username = USERNAME

    password = PasswordField('New password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match!')
    ])
    confirm = PasswordField('New password again')

    submit = SubmitField('Reset password')
