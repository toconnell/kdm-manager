"""

    Everything in Models.py belongs here and will eventually be moved here.

"""

from utils import email_exception


def log_event_exception_manager(log_event_call):
    """
    This is meant to decorate Models.UserAsset.log_event() calls ONLY, i.e.
    it should not be used to decorate other methods.

    The basic idea here is to capture exceptions, log them, email them and NOT
    interrupt the request. This is really the only method where we ever want to
    handle exceptions this way.

    """

    def wrapper(self, *args, **kwargs):

        """ Wraps the incoming call. """

        try:
            return log_event_call(self, *args, **kwargs)
        except Exception as log_event_call_exception:
            err_msg = "Unhandled exception in log_event() method!"
            err_msg += "args: %s, kwargs: %s" % (args, kwargs)
            self.logger.exception(err_msg)
            email_exception(log_event_call_exception)

    return wrapper
