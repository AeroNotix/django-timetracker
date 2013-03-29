'''
On the month end close we total up all overtime values and send out a report
to managers of an account.
'''

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import csv
import codecs
import datetime
import calendar

from django.core.management.base import BaseCommand, CommandError
from django.core import mail
from django.http import HttpResponse

from timetracker.tracker.models import Tbluser, TrackingEntry
from timetracker.utils.writers import UnicodeWriter
from timetracker.utils.datemaps import round_down, WORKING_CHOICES


connection = mail.get_connection()


def report_for_account(account, now, send=True):
    '''Sends all overtime reports to the managers of an account for a given
    date.'''
    DAYS_SHORT = [element[0]
                  for element in WORKING_CHOICES
                  if element[0] != "SATUR"] + ["ROVER"]
    buff = StringIO()
    buff.write("\xef\xbb\xbf")
    csvout = UnicodeWriter(buff, delimiter=';')
    users = Tbluser.objects.filter(market=account, disabled=False).order_by("lastname")

    # generate the dates for this month
    c = calendar.Calendar()
    dates = filter(
    lambda date: date.month == now.month,
    c.itermonthdates(now.year, now.month)
    )

    csvout.writerow(
        # write out the top heading
        ["Date"] + [user.rev_name() for user in users]
        )
    csvout.writerow(
        # write out the settlement period row.
        ["Settlement Period"] + [user.job_code[-1]
                                 if user.job_code else ""
                                 for user in users]
        )
    csvout.writerow(
        # write out the e-mail row.
        ["EmployeeID"] + [user.user_id for user in users]
        )
    csvout.writerow(
        # write out the total balances.
        ["Balance"] + ['="'+str(user.get_total_balance(ret='flo',
                                                       year=now.year,month=now.month))+'"'
                       for user in users]
        )
    for date in dates:
        current_line = [str(date)]
        for user in users:
            try:
                entry = TrackingEntry.objects.get(
                    user_id=user.id,
                    entry_date=date
                )
            except TrackingEntry.DoesNotExist:
                current_line.append("")
                continue
            if entry.daytype not in DAYS_SHORT:
                current_line.append("")
                continue
            # if the entry is a return for overtime entry, we display
            # the user's shiftlength as a negative value since that's
            # what the value should be.
            value = round_down(entry.time_difference() if entry.daytype != "ROVER" else -entry.total_working_time())
            current_line.append('="'+str(value)+'"' if value != 0 else "")
        csvout.writerow(current_line)

    csvfile = buff.getvalue()
    if send:
        message = mail.EmailMessage(from_email="timetracker@unmonitored.com")
        message.body = \
                       "Hi,\n\n" \
                       "Please see attached your month end overtime report for " \
                       "your team.\n\n" \
                       "If there are any errors, please inform the administrator " \
                       "of the timetracker immediately.\n\n" \
                       "Regards,\n" \
                       "Timetracker team"

        message.attach(
            "overtimereport.csv",
            csvfile,
            "application/octet-stream"
        )
        message.to = ["aaron.france@hp.com"] + \
                     Tbluser.administrator_emails_for_account(account)
        message.subject = "End of month Overtime Totals."
        message.send()
    else:
        response = HttpResponse(csvfile, mimetype="text/csv")
        response['Content-Disposition'] = \
            'attachment;filename=MEC_OT_Report_%s.csv' % now
        return response

def get_previous_month(d):
    '''From one date we return the first day of the previous month.

    :param d: :class:`datetime.date`
    '''
    first_day_of_current_month = d.replace(day=1)
    last_day_of_previous_month = (first_day_of_current_month -
                                  datetime.timedelta(days=1))
    return last_day_of_previous_month.replace(day=1)

class Command(BaseCommand):
    '''Implementation of a Django command.'''
    help = 'Sends notifications of overtime balances to the all those ' \
           'who have balances over zero hours.'

    def handle(self, *args, **options):
        '''Entry point for the command.'''
        for account in args:
            d = get_previous_month(datetime.datetime.now())
            report_for_account(account, d)
