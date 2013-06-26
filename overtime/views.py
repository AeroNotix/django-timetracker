'''Views which are mapped from the URL objects in urls.py

    .. moduleauthor:: Aaron France <aaron.france@hp.com>

    :platform: All
    :synopsis: Module which contains view functions that are mapped from urls
'''

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

from timetracker.tracker.models import Tbluser, UserForm, TrackingEntry
from timetracker.tracker.models import Tblauthorization as tblauth
from timetracker.tracker.forms import TrackingEntryForm

from timetracker.utils.decorators import admin_check, loggedin
from timetracker.loggers import suspicious_log, email_log, error_log

@admin_check
def accept_edit(request, entry):
    auth_user = Tbluser.objects.get(
        id=request.session.get("user_id")
    )
    # if the provided entry ID is not here, then we're being duped.
    try:
        entry = TrackingEntry.objects.get(id=entry)
    except:
        suspicious_log.critical(
            "An accept/edit check was made by %s for a non-existent entry." % auth_user.name()
        )
        raise Http404

    if not entry.user_can_see(auth_user):
        raise Http404

    return render_to_response(
        "accept_edit.html",
        {
            "entry": entry,
            "form": TrackingEntryForm(instance=entry)
        },
        RequestContext(request)
    )

def delete(request, entry):
    return HttpResponse("sup")

def accepted(request):
    return HttpResponse("sup")
