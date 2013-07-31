import datetime
import os
import imp

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.core.urlresolvers import reverse

from timetracker.utils.decorators import loggedin, json_response
from timetracker.vcs.models import ActivityEntry, Activity
from timetracker.vcs.activities import (defaultplugins,
                                        listplugins,
                                        pluginbyname,
                                        serialize_activityentry)
from timetracker.tracker.models import Tbluser

@loggedin
def vcs(request): # pragma: no cover
    user = request.session.get("user_id")
    user = Tbluser.objects.get(id=user)
    return render_to_response(
        "vcs.html",
        {
            "todays_date": datetime.datetime.today().strftime("mm-dd-yyyy"),
            "plugin_dict": defaultplugins(acc=user.market),
        },
        RequestContext(request)
    )

@loggedin
def vcs_add(request):
    activity_key = request.POST.get("activity_key")
    amount = request.POST.get("amount")
    date = request.POST.get("date")
    user_id = request.session.get("user_id")

    if not all([date, user_id, activity_key, amount]):
        raise Http404

    activity = Activity.objects.get(id=activity_key)
    user = Tbluser.objects.get(id=user_id)
    ActivityEntry(user=user,
                  activity=activity,
                  amount=amount,
                  creation_date=date).save()

    return HttpResponseRedirect(reverse("timetracker.vcs.views.vcs"))

@loggedin
@json_response
def entries(request): # pragma: no cover
    user_id = request.session.get("user_id")
    user = Tbluser.objects.get(id=user_id)
    date = request.GET.get("date")
    if not date:
        raise Http404
    entries = ActivityEntry.objects.filter(creation_date=date)
    if not len(entries):
        raise Http404
    return {"entries": map(serialize_activityentry, entries)}

@loggedin
@json_response
def update(request):
    '''Update is the handler for when an ActivityEntry is to be updated by
    the front-end. We're simply changing the Volume field on the
    ActivityEntry.
    '''

    volume = request.POST.get("volume")
    entryid = request.POST.get("id")
    if not volume or not entryid:
        raise Http404
    try:
        entry = ActivityEntry.objects.get(id=entryid)
    except ActivityEntry.DoesNotExist:
        return {"success": False}

    if int(volume) == 0:
        entry.delete()
    else:
        entry.amount = int(volume)
        entry.save()
    return {"success": True}

@loggedin
def report_upload(request): # pragma: no cover
    '''report_upload is the handler for when a report is requested to be
    processed. It will extract the processor name from the POST body
    along with the file. We then look for the associated report
    processor and pass the file upload to that processor for
    miscellanious processing.
    '''

    # Get a fd on the in-memory uploaded file.
    fd = request.FILES.get("uploaded_file")
    user_id = request.session.get("user_id")
    user = Tbluser.objects.get(id=user_id)
    processor = pluginbyname(request.POST.get("processor"), acc=user.market)
    if not processor:
        raise Http404
    # call the dynamically loaded plugin with the fd.
    success = processor["callback"](fd)
    if success["success"]:
        return HttpResponse("Done! %s" % success["data"])
    return HttpResponse("Error processing report: %s" % success["error"])
