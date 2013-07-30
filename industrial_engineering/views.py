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
        year = datetime.today().year
        month = datetime.today().month
    return year, month

@permissions(["INENG"])
def costbuckets(request):
    year, month = getmonthyear(request)
    kwargs = {"year": year,
              "month": month}
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
            "year": year,
            "months": generate_month_box(id="month"),
            "selected_month": month,
            "selected_team": request.GET["team"] if request.GET.get("team") else "AD",
            "costbuckets": cbb,
            "current": " %s/%s" % (year, month)
        },
        RequestContext(request)
    )

@permissions(["INENG"])
def utilization(request):
    year, month = getmonthyear(request)
    kwargs = {"year": year,
              "month": month}

    theteam = request.GET.get("team")
    teamselection = group_for_team(theteam) if theteam else MARKET_CHOICES_LIST
    utlztn, dates = ActivityEntry.utilization_last_12_months(teamselection, **kwargs)
    team = MARKET_CHOICES_MAP[request.GET["team"]] \
           if request.GET.get("team") else "All teams"
    return render_to_response(
        "industrial_engineering_utilization.html",
        {
            "teams": MARKET_CHOICES,
            "team": team,
            "year": year,
            "months": generate_month_box(id="month"),
            "selected_month": month,
            "selected_team": request.GET["team"] if request.GET.get("team") else "AD",
            "current": " %s/%s" % (year,month),
            "utlztn": utlztn[datetime(year=year,month=month,day=1)],
            "utlztn_all": utlztn,
            "dates": [date.strftime("%B") for date in dates]
        },
        RequestContext(request)
    )
