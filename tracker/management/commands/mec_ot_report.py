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
from timetracker.tracker.models import *
from timetracker.utils.writers import UnicodeWriter

connection = mail.get_connection()


def send_report_for_account(account, now):
    '''Sends all overtime reports to the managers of an account for a given
    date.'''
    message = mail.EmailMessage(from_email="timetracker@unmonitored.com")
    message.body = \
        "Hi,\n\n" \
        "Please see attached your month end overtime report for " \
        "your team.\n\n" \
        "If there are any errors, please inform the administrator " \
        "of the timetracker immediately.\n\n" \
        "Regards,\n" \
        "Timetracker team"

    buff = StringIO()
    buff.write("\xef\xbb\xbf")
    csvout = UnicodeWriter(buff, delimiter=';')
    users = filter(
        lambda user: user.get_total_balance(ret='num') == 0,
        Tbluser.objects.filter(market=account, disabled=False)
        )

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
        ["Balance"] + [str(user.get_total_balance(ret='num'))
                       for user in users]
        )
    for date in dates:
        current_line = [str(date)]
        for user in users:
            try:
                entry = TrackingEntry.objects.get(user_id=user.id,
                                                  entry_date=date)
            except TrackingEntry.DoesNotExist:
                current_line.append("")
                continue

            if entry.is_overtime():
                current_line.append(0-entry.time_difference())
            else:
                current_line.append("")
        csvout.writerow(current_line)

    csvfile = buff.getvalue()
    message.attach(
        "overtimereport.csv",
        csvfile,
        "application/octet-stream"
        )
    message.to = ["aaron.france@hp.com"] + \
        Tbluser.administrator_emails_for_account(account)
    message.subject = "End of month Overtime Totals."
    message.send()

def get_previous_month(d):
    '''From one date we return the first day of the previous month.

    :param d: :class:`datetime.date`
    '''
    first_day_of_current_month = d.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    return last_day_of_previous_month.replace(day=1)

class Command(BaseCommand):
    '''Implementation of a Django command.'''
    help = 'Sends notifications of overtime balances to the all those ' \
           'who have balances over zero hours.'

    def handle(self, *args, **options):
        '''Entry point for the command.'''
        for account in args:
            d = get_previous_month(datetime.datetime.now())
            send_report_for_account(account, d)
