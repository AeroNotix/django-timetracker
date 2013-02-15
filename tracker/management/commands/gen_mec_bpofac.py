try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import csv
import datetime
import calendar

from django.core.management.base import BaseCommand, CommandError
from django.core import mail
from timetracker.tracker.models import *

connection = mail.get_connection()


class Command(BaseCommand):
    help = 'Sends notifications of overtime balances to the all those ' \
           'who have balances over zero hours.'

    def handle(self, *args, **options):
        message = mail.EmailMessage(from_email="timetracker@unmonitored.com")
        message.body = \
            "Hi,\n\n" \
            "Please see attached your month end overtime report for " \
            "your team.\n\n" \
            "If there are any errors, please inform the administrator" \
            "of the timetracker immediately.\n\n" \
            "Regards,\n" \
            "Timetracker team"

        buff = StringIO()
        csvout = csv.writer(buff, delimiter=';')
        users = filter(
            lambda user: user.get_total_balance(ret='num') == 0,
            Tbluser.objects.filter(market="BF", disabled=False)
            )

        # generate the dates for this month
        c = calendar.Calendar()
        now = datetime.datetime.now()
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
            ["Settlement Period"] + [user.job_code[-1] if user.job_code else "" for user in users]
            )
        csvout.writerow(
            # write out the e-mail row.
            ["EmployeeID"] + [user.user_id for user in users]
            )
        csvout.writerow(
            # write out the total balances.
            ["Balance"] + [user.get_total_balance(ret='num') for user in users]
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
        message.to = ["aaron.france@hp.com"]#, "ulrich.schroeder@hp.com"]
        message.subject = "End of month Overtime Totals."
        message.send()
