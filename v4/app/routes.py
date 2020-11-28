"""

    The main routes for version four of the kdm-manager app.

    We DO NOT use blueprints and are intentionally tying to minimize endpoints
    in this app, so this is the main event.

"""

# standard library

# second party imports
import flask
import flask_login

# kdm-manager imports
from app import app, utils
from app.forms import LoginForm, ResetForm
from app.models import users


#   front matter
app.logger = utils.get_logger()


#
#   login / logout / register / reset
#
@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    """ Formerly the stand-alone AngularJS login app; now a part of the unified
    Flask application. """

    # 1.) check to see if we're resetting a PW and redirect if so
    if flask.request.args.get('recover_password', None) is not None:
        return flask.redirect(
            flask.url_for(
                'reset_password',
                login = flask.request.args.get('login', None),
                recovery_code = flask.request.args.get('recovery_code', None),
            )
        )

    # 2.) if we're already logged in, forward us to the dash
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('dashboard'))

    # 3.) process the form, see if it validates
    login_form = LoginForm()
    if login_form.validate_on_submit():

        # try to authenticate the user against the API
        user = users.User(
            username = login_form.username.data,
            password = login_form.password.data
        )

        if user.login_to_api(): # returns True if the user authenticates
            return user.login_to_flask(login_form)
        else:
            flask.flash('Invalid username or password!')
            return flask.redirect(flask.url_for('login'))

    return flask.render_template(
        'login/sign_in.html',
        form = login_form,
        **app.config
    )


@flask_login.login_required
@app.route('/logout')
def logout():
    """ Kills the flask_login 'session' and returns the user to the login. """
    flask_login.logout_user()
    redirect = flask.redirect(flask.url_for('login'))
    response = app.make_response(redirect)
    response.set_cookie('kdm-manager_token', 'None')
    return response


#
#   REGISTER TK
#

@app.route('/reset_password/<login>/<recovery_code>', methods=['GET','POST'])
def reset_password(login, recovery_code):
    """ Processes the form for resetting a pw. """

    reset_form = ResetForm()
    reset_form.default_login = login    # bit of a jinja hack here

    if flask.request.method == 'POST' and reset_form.validate():
        user = users.User(username=reset_form.username.data)
        reset_result = user.reset_password(
            new_password = reset_form.password.data,
            recovery_code = recovery_code
        )

        # user.reset_password() logs the user in to the API, so we should have
        #an _id and a self.token now, which we can use to log in to flask

        if user.has_token():
            return user.login_to_flask(reset_form)
        else:
            flask.flash(reset_result)

    return flask.render_template(
        'login/reset_password.html',
        form = reset_form,
        **app.config
    )


@app.route('/help')
def help():
    """ Really simple; just renders the help and the controls for triggering
    a password reset. """
    return flask.render_template(
        'login/help.html',
        **app.config
    )



#
#   Static and media routes for dev use!
#

@app.route('/favicon.ico')
def favicon():
    """ Returns the favicon when working in dev. """
    return flask.send_from_directory('static/images', 'favicon.png')

@app.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    """ Returns the static dir when working in dev. """
    return flask.send_from_directory("static/%s" % sub_dir, path)
