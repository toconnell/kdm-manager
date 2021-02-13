"""

    The main routes for version four of the kdm-manager app.

    We DO NOT use blueprints and are intentionally tying to minimize endpoints
    in this app, so this is the main event.

"""

# standard library

# second party imports
import flask
import flask_login
import requests

# kdm-manager imports
from app import app, utils
from app.forms import LoginForm, RegisterForm, ResetForm
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

#    flask.abort(500, 'This is the error!')
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


@app.route('/logout')
#@flask_login.login_required
def logout():
    """ Kills the flask_login 'session' and returns the user to the login. """
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route('/register', methods=['GET','POST'])
def register():
    """ Processes the form for registering a new user with the API. """

    register_form = RegisterForm()

    if flask.request.method == 'POST' and register_form.validate():
        user = users.User(
            username=register_form.username.data,
            password=register_form.password.data
        )
        success, api_response = user.new()
        if success:
            flask.flash('New user registration successful! Please sign in...')
            return flask.redirect(flask.url_for('login'))
        else:
            flask.flash(api_response)

    # if we tried and failed validation, default in the email we tried
    if register_form.username.data is not None:
        register_form.default_login = register_form.username.data

    return flask.render_template(
        'login/register.html',
        form = register_form,
        **app.config
    )


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


@app.route('/about')
def about():
    """ This is currently just a flat page, but we might do some GDPR cookie
    complaiance stuff here eventually, so it's its own endpoint. """
    return flask.render_template(
        'login/about.html',
        **app.config
    )




#
#   views!  (at least, that's what we used to call them)
#

@app.route('/dashboard')
@flask_login.login_required
def dashboard():
    prefs = users.Preferences()
    return flask.render_template(
        'dashboard/index.html',
        PREFERENCES = prefs.dump(),
        **app.config
    )

@app.route('/new')
@flask_login.login_required
def new_settlement():
    prefs = users.Preferences()
    return flask.render_template(
        'new_settlement.html',
        **app.config
    )



#
#   error handling
#
@app.errorhandler(500)
def server_explosion(error_msg):
    """ We sometimes throw a flask.abort(500). """
    return flask.render_template(
        'server_explosion.html',
        error=error_msg,
        request=flask.request,
        **app.config
    ), 500


@app.errorhandler(utils.Logout)
def force_logout(error_msg):
    """ When the Flask error handler catches a utils.Logout, we need to log
    the user out immediately. """
    #flask.flash(error_msg)
    return flask.redirect(flask.url_for('logout'))


#
#   Static and media routes for dev use!
#

@app.route('/favicon.ico')
def favicon():
    """ Returns the favicon when working in dev. """
    return flask.send_file('static/media/favicon.ico')

@app.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    """ Returns the static dir when working in dev. """
    return flask.send_from_directory("static/%s" % sub_dir, path)
