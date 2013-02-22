try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import datetime
import csv

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404

from timetracker.utils.decorators import admin_check, loggedin
from timetracker.tracker.models import Tbluser, TrackingEntry
from timetracker.tracker.models import Tblauthorization as tblauth
from timetracker.utils.datemaps import generate_employee_box, generate_month_box, MONTH_MAP
from timetracker.utils.writers import UnicodeWriter

@admin_check
def reporting(request):
    user = Tbluser.objects.get(id=request.session.get("user_id"))
    return render_to_response(
        "reporting.html",
        {
            "employee_box": generate_employee_box(user),
            "yearbox_hol": datetime.datetime.now().year,
            "monthbox_hol": generate_month_box("monthbox_hol"),
            "monthbox_ot": generate_month_box("monthbox_ot"),
            "monthbox_hr": generate_month_box("monthbox_hr"),
        },
        RequestContext(request))

@admin_check
def download_all_holiday_data(request, who=None):
    if not who:
        raise Http404

    auth_user = Tbluser.objects.get(id=request.session.get("user_id"))
    try:
        target_user = auth_user.get_subordinates().get(id=who)
    except Tbluser.DoesNotExist:
        raise Http404

    buf = StringIO()
    buf.write("\xef\xbb\xbf")
    csvfile = UnicodeWriter(buf)
    csvfile.writerow(TrackingEntry.headings())

    for entry in TrackingEntry.objects.filter(user_id=who):
        csvfile.writerow(entry.display_as_csv())

    response = HttpResponse(buf.getvalue(), mimetype="text/csv")
    response['Content-Disposition'] = \
        'attachment;filename=AllHolidayData_%s.csv' % target_user.id
    return response

@admin_check
def yearmonthhol(request, year=None, month=None):
    auth_user = Tbluser.objects.get(id=request.session.get("user_id"))
    buf = StringIO()
    buf.write("\xef\xbb\xbf")
    csvfile = UnicodeWriter(buf)
    csvfile.writerow(TrackingEntry.headings())
    for user in auth_user.get_subordinates():
        for entry in TrackingEntry.objects.filter(
            entry_date__year=year,
            entry_date__month=month,
            user_id=user.id):
            csvfile.writerow(entry.display_as_csv())
    response = HttpResponse(buf.getvalue(), mimetype="text/csv")
    response['Content-Disposition'] = \
        'attachment;filename=HolidayData_%s_%s.csv' % (year, month)
    return response

@admin_check
def ot_by_month(request, year=None, month=None):
    auth_user = Tbluser.objects.get(id=request.session.get("user_id"))
    buf = StringIO()
    buf.write("\xef\xbb\xbf")
    csvfile = UnicodeWriter(buf)
    csvfile.writerow(
        ["Name", "Team", MONTH_MAP[int(month)-1][1]]
        )
    total_balance = 0
    for user in auth_user.get_subordinates():
        balance = user.get_total_balance(ret='flo', year=year, month=month)
        total_balance += balance
        csvfile.writerow([user.name(), user.process, "%.2f" % balance])
    csvfile.writerow(["Total", "Total", "%.2f" % total_balance])
    response = HttpResponse(buf.getvalue(), mimetype="text/csv")
    response['Content-Disposition'] = \
        'attachment;filename=OT_By_Month_%s_%s.csv' % (year, month)
    return response

@admin_check
def ot_by_year(request, year=None):
    auth_user = Tbluser.objects.get(id=request.session.get("user_id"))
    buf = StringIO()
    buf.write("\xef\xbb\xbf")
    csvfile = UnicodeWriter(buf)
    csvfile.writerow(
        ["Name", "Team"] + [MONTH_MAP[n][1] for n in range(0,12)]
        )
    total_balance = 0
    balances = {
        n: 0 for n in range(1, 13)
        }
    for user in auth_user.get_subordinates():
        row = [user.name(), user.process]
        for month in range(1, 13):
            balance = user.get_total_balance(ret='flo', year=year, month=month)
            balances[month] += balance
            row.append("%.2f" % balance if balance != 0.0 else "-")
        csvfile.writerow(row)
    totalrow = ["Total", "Total"]
    [totalrow.append("%.2f" % balances[n]) for n in range(1,13)]
    csvfile.writerow(totalrow)
    response = HttpResponse(buf.getvalue(), mimetype="text/csv")
    response['Content-Disposition'] = \
        'attachment;filename=OT_By_Month_%s_%s.csv' % (year, month)
    return response
