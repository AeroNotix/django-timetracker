from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from timetracker.utils.decorators import permissions
from timetracker.utils.datemaps import MARKET_CHOICES, group_for_team, generate_month_box

from timetracker.vcs.models import ActivityEntry

@permissions(["INENG"])
def costbuckets(request):
    try:
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
    except ValueError:
        raise Http404
    except TypeError:
        year = None
        month = None

    kwargs = {"year": year if year else None,
            "month": month if month else None}
    if request.GET.get("team"):
        costbuckets = ActivityEntry.costbucket_count(group_for_team(request.GET["team"]), **kwargs)
    else:
        costbuckets = ActivityEntry.costbucket_count([c[0] for c in MARKET_CHOICES], **kwargs)
    team = {c[0]: c[1] for c in MARKET_CHOICES}[request.GET["team"]] \
                                                if request.GET.get("team") else "All teams"
    return render_to_response(
        "industrial_engineering_reports.html",
        {
            "teams": MARKET_CHOICES,
            "team": team,
            "year": year if year else datetime.now().year,
            "months": generate_month_box(id="month"),
            "selected_month": month if month else datetime.today().month,
            "selected_team": request.GET["team"] if request.GET.get("team") else "AD",
            "costbuckets": costbuckets,
            "current": " %s/%s" % (year if year else datetime.today().year,
                                   month if month else datetime.today().month)
        },
        RequestContext(request)
    )
