from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from timetracker.utils.decorators import loggedin

@loggedin
def vcs(request):
    return render_to_response(
        "vcs.html",
        {},
        RequestContext(request)
    )
