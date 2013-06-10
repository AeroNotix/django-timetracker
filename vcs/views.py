import datetime

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from timetracker.utils.decorators import loggedin
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
    user_id = request.session.get("user_id")

    if not activity_key or not amount:
        raise Http404

    activity = Activity.objects.get(id=activity_key)
    user = Tbluser.objects.get(id=user_id)
    ActivityEntry(user=user, activity=activity, amount=amount).save()

    return render_to_response(
        "vcs.html",
        {},
        RequestContext(request)
    )
