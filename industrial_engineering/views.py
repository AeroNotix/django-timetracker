from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from timetracker.utils.decorators import permissions
from timetracker.utils.datemaps import (MARKET_CHOICES, MARKET_CHOICES_MAP,
                                        MARKET_CHOICES_LIST, group_for_team,
                                        generate_month_box)

from timetracker.vcs.models import ActivityEntry

def getmonthyear(request):
    try:
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
    except ValueError:
        raise Http404
    except TypeError:
        year = None
        month = None
    return year, month

@permissions(["INENG"])
def costbuckets(request):
    year, month = getmonthyear(request)
    kwargs = {"year": year if year else None,
              "month": month if month else None}
    if request.GET.get("team"):
        cbb = ActivityEntry.costbucket_count(group_for_team(request.GET["team"]), **kwargs)
    else:
        cbb = ActivityEntry.costbucket_count(MARKET_CHOICES_LIST, **kwargs)
    team = MARKET_CHOICES_MAP[request.GET["team"]] \
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
            "costbuckets": cbb,
            "current": " %s/%s" % (year if year else datetime.today().year,
                                   month if month else datetime.today().month)
        },
        RequestContext(request)
    )

@permissions(["INENG"])
def utilization(request):
    year, month = getmonthyear(request)
    kwargs = {"year": year if year else None,
              "month": month if month else None}

    if request.GET.get("team"):
        utlztn = ActivityEntry.utilization_calculation(group_for_team(request.GET["team"]), **kwargs)
    else:
        utlztn = ActivityEntry.utilization_calculation(MARKET_CHOICES_LIST, **kwargs)

    team = MARKET_CHOICES_MAP[request.GET["team"]] \
           if request.GET.get("team") else "All teams"

    return render_to_response(
        "industrial_engineering_utilization.html",
        {
            "teams": MARKET_CHOICES,
            "team": team,
            "year": year if year else datetime.now().year,
            "months": generate_month_box(id="month"),
            "selected_month": month if month else datetime.today().month,
            "selected_team": request.GET["team"] if request.GET.get("team") else "AD",
            "current": " %s/%s" % (year if year else datetime.today().year,
                                   month if month else datetime.today().month),
            "utlztn": utlztn
        },
        RequestContext(request)
    )
