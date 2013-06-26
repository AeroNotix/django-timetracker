'''Views which are mapped from the URL objects in urls.py

    .. moduleauthor:: Aaron France <aaron.france@hp.com>

    :platform: All
    :synopsis: Module which contains view functions that are mapped from urls
'''

from functools import wraps

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect

from timetracker.overtime.models import PendingApproval
from timetracker.tracker.models import Tbluser, TrackingEntry
from timetracker.tracker.models import Tblauthorization as tblauth
from timetracker.tracker.forms import TrackingEntryForm

from timetracker.utils.decorators import admin_check, loggedin
from timetracker.loggers import suspicious_log, email_log, error_log

def overtimereqs(f):
    @wraps(f)
    def inner(request, *args, **kwargs):
        entry = kwargs.get("entry")
        if not entry:
            return f(request, *args, **kwargs)
        auth_user = Tbluser.objects.get(
            id=request.session.get("user_id")
        )
        # if the provided entry ID is not here, then we're being duped.
        try:
            entry = PendingApproval.objects.get(entry_id=entry, closed=False)
        except PendingApproval.DoesNotExist:
            suspicious_log.critical(
                "An accept/edit check was made by %s for a non-existent entry." % auth_user.name()
            )
            raise Http404
        if not entry.entry.user_can_see(auth_user):
            raise Http404
        return f(request, *args, **kwargs)
    return inner

@overtimereqs
@admin_check
def accept_edit(request, entry):
    entry = PendingApproval.objects.get(entry_id=entry, closed=False)
    return render_to_response(
        "accept_edit.html",
        {
            "entry": entry,
            "form": TrackingEntryForm(instance=entry.entry)
        },
        RequestContext(request)
    )

@admin_check
def accepted(request):
    status = request.POST["status"] == "approved"
    pending_id = request.POST.get("pending_id")
    PendingApproval.objects.get(id=pending_id).close(status)
    return render_to_response(
        "accept_edit_done.html",
        {
            "status": status
        },
        RequestContext(request)
    )
