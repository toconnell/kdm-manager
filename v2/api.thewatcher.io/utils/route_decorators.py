"""

    We manage all API route decorators here, including the following:

        - crossdomain() which is used to add allowed headers to routes

    Anything method that decorates a route can live here.

"""

from datetime import timedelta
import functools

import flask

from api import settings


def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):

    """ This decorates routes and adds allowed headers, etc. to them. """

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()


    def get_methods():

        """ Call this to process the methods kwarg; defaults to the
        flask.current_app allowed headers if methods kwarg is None."""

        if methods is not None:
            return methods

        options_resp = flask.current_app.make_default_options_response()
        return options_resp.headers['allow']


    def decorator(func):

        """ This method decorates the incoming method, which should be a
        route from Flask. """

        def wrapped_function(*args, **kwargs):

            """ Generic wrapper for the incoming func. """

            if automatic_options and flask.request.method == 'OPTIONS':
                resp = flask.current_app.make_default_options_response()
            else:
                resp = flask.make_response(func(*args, **kwargs))
            if not attach_to_all and flask.request.method != 'OPTIONS':
                return resp

            resp.headers['Access-Control-Allow-Origin'] = origin
            resp.headers['Access-Control-Allow-Methods'] = get_methods()
            resp.headers['Access-Control-Max-Age'] = str(max_age)

            if headers is not None:
                resp.headers['Access-Control-Allow-Headers'] = headers
            elif headers is None:
                default_headers = settings.get('api','default_headers')
                resp.headers['Access-Control-Allow-Headers'] = default_headers

            return resp

        func.provide_automatic_options = False
        return functools.update_wrapper(wrapped_function, func)


    #
    #   Finally, return the decorator.
    #

    return decorator
