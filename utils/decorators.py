# pylint: disable=E1101
'''
Module to for sharing decorators between all modules
'''
from functools import wraps
import simplejson

from django.http import HttpResponse, Http404

from timetracker.tracker.models import Tbluser
from timetracker.loggers import info_log, suspicious_log


def loggedin(func):

    """Decorator to make sure that the view is being accessed by a
    logged in user.

    This works by simply checking that the user_id in the session
    table is 1) There and 2) A real user. If either of these aren't
    satisfied we throw back a 404.

    We also log this.

    :param func: A function which has a request object as a parameter
    :returns: Nothing directly, it returns the function it decorates
    :raises: :class:`Http404` error
    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        '''implementation'''
        try:
            Tbluser.objects.get(id=request.session.get("user_id"))
        except Tbluser.DoesNotExist:
            info_log.info("Non-logged in user accessing @loggedin page")
            raise Http404
        return func(request, *args, **kwargs)
    return inner


def admin_check(func):

    """Wrapper to see if the view is being called as an admin

    This works by 1) Checking if there is a user_id in the session
    table. 2) If that user is a real user in the database and 3) if
    that user's is_admin() returns True.

    :param func: A function with a request object as a parameter
    :returns: Nothing directly, it returns the function it decorates.
    :raises: :class:`Http404` error
    """

    @wraps(func)
    def inner(request, **kwargs):
        '''implementation'''
        try:
            user = Tbluser.objects.get(
                id=request.session.get('user_id', None)
            )
        except Tbluser.DoesNotExist:
            info_log.info("Non-logged in user accessing @loggedin page")
            raise Http404
        if not user.sup_tl_or_admin():
            suspicious_log.info("Non-admin user accessing @admin_check page")
            raise Http404
        else:
            return func(request, **kwargs)

    return inner


def json_response(func):

    """
    Decorator function that when applied to a function which
    returns some json data will be turned into a HttpResponse

    This is useful because the call site can literally just
    call the function as it is without needed to make a http-
    response.

    :param func: Function which returns a dictionary
    :returns: :class:`HttpResponse` with mime/application as JSON
    """

    @wraps(func)
    def inner(request):

        """
        Grabs the request object on the decorated and calls
        it
        """

        return HttpResponse(simplejson.dumps(func(request)),
                            mimetype="application/javscript")
    return inner


def request_check(func):

    """Decorator to check an incoming request against a few rules

    This function should decorate any function which is supposed
    to be accessed by and only by Ajax. If we see that the function
    was accessed by any other means, we raise a :class:`Http404`
    and give up processing the page.

    We also make a redundant check to see if the user is logged in.

    :param func: Function which has a request object parameter.
    :returns: The function which it decorates.
    :raises: :class:`Http404`
    """

    @wraps(func)
    def inner(request):
        """
        Pulls the request object off the decorated function
        """
        if not request.is_ajax():
            suspicious_log.info("Request check made on non-ajax call")
            raise Http404
        if not request.session.get('user_id', None):
            # if there is no user id in the session
            # something weird is going on
            suspicious_log.info("Ajax call made by a non-logged in entity")
            raise Http404
        return func(request)
    return inner
