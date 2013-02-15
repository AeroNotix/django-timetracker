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

connection = mail.get_connection()


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    Taken from the python documentation.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def send_report_for_account(account):
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
    buff.write("\xef\xbb\xbf")
    csvout = UnicodeWriter(buff, delimiter=';')
    users = filter(
        lambda user: user.get_total_balance(ret='num') == 0,
        Tbluser.objects.filter(market=account, disabled=False)
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


class Command(BaseCommand):
    help = 'Sends notifications of overtime balances to the all those ' \
           'who have balances over zero hours.'

    def handle(self, *args, **options):
        for account in args:
            send_report_for_account(account)
