import datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from timetracker.utils.decorators import loggedin, json_response
from timetracker.vcs.models import ActivityEntry, Activity
from timetracker.tracker.models import Tbluser

@loggedin
def vcs(request):
    return render_to_response(
        "vcs.html",
        {"todays_date": datetime.datetime.today().strftime("mm-dd-yyyy")},
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
    ActivityEntry(user=user, activity=activity, amount=amount, creation_date=date).save()

    return render_to_response(
        "vcs.html",
        {},
        RequestContext(request)
    )

@loggedin
@json_response
def entries(request):
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
    volume = request.POST.get("volume")
    entryid = request.POST.get("id")
    if not volume or not entryid:
        raise Http404
    print request.POST
    entry = ActivityEntry.objects.get(id=entryid)
    entry.amount = int(volume)
    entry.save()
    return {"success": True}

def serialize_activityentry(entry):
    return {
        "id": entry.id,
        "date": str(entry.creation_date),
        "text": entry.activity.groupdetail,
        "amount": int(entry.amount)
    }
