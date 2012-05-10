'''
Module to for sharing decorators between all modules
'''

import simplejson

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from timetracker.tracker.models import Tbluser


def loggedin(func):

    """
    Decorator to make sure that the view is being accessed
    by a logged in user
    """

    def inner(request, *args, **kwargs):
        try:
            get_object_or_404(Tbluser, id=request.session.get("user_id"))
        except Tbluser.DoesNotExist:
            raise Http404
        except TypeError:
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
            raise Http404
        if not user.is_admin():
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
            raise Http404

        if not request.session.get('user_id', None):
            # if there is no user id in the session
            # something weird is going on
            raise Http404

        return func(request)

    return inner
