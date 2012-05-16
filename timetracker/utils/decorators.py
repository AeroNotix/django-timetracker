'''
Module to for sharing decorators between all modules
'''

import simplejson

from django.http import HttpResponse, Http404

from timetracker.tracker.models import Tbluser
from timetracker.loggers import (debug_log, info_log,
                                 email_log, database_log,
                                 error_log, suspicious_log)


def loggedin(func):

    """
    Decorator to make sure that the view is being accessed
    by a logged in user
    """

    def inner(request, *args, **kwargs):
        try:
            Tbluser.objects.get(id=request.session.get("user_id"))
        except Tbluser.DoesNotExist:
            info_log.info("Non-logged in user accessing @loggedin page")
            raise Http404
        return func(request, *args, **kwargs)

    return inner


def admin_check(func):

    """
    Wrapper to see if the view is being called as an admin
    """

    def inner(request, **kwargs):

        try:
            user = Tbluser.objects.get(
                id=request.session.get('user_id', None)
            )
        except Tbluser.DoesNotExist:
            info_log.info("Non-logged in user accessing @loggedin page")
            raise Http404
        if not user.is_admin():
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
    """

    def inner(request):

        """
        Grabs the request object on the decorated and calls
        it
        """

        return HttpResponse(simplejson.dumps(func(request)),
                            mimetype="application/javscript")
    return inner


def request_check(func):

    """
    Decorator to check an incoming request against a few rules
    """

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
