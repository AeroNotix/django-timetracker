from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from timetracker.utils.decorators import permissions
from timetracker.utils.datemaps import MARKET_CHOICES, group_for_team

from timetracker.vcs.models import ActivityEntry

@permissions(["INENG"])
def reporting(request):
    if request.GET.get("team"):
        print 'here'
        costbuckets = ActivityEntry.costbucket_count(group_for_team(request.GET["team"]))
    else:
        costbuckets = ActivityEntry.costbucket_count([c[0] for c in MARKET_CHOICES])
    return render_to_response(
        "industrial_engineering_reports.html",
        {
            "teams": MARKET_CHOICES,
            "team": request.GET["team"] if request.GET.get("team") else "All teams",
            "year": datetime.now().year,
            "costbuckets": costbuckets
        },
        RequestContext(request)
    )
