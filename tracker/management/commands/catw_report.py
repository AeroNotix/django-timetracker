'''
Script to generate CATW reports from the data in the Timetracking
database.

Currently in the prototype stage, queries need to be optimized and
datastructures used may not be optimal. However, it conforms to-spec
and is in-use.
'''
import datetime
import csv
import calendar
from optparse import make_option

from timetracker.tracker.models import Tbluser, TrackingEntry
from django.core.management.base import BaseCommand


QUERIES = 0
CHOICES = [
    (["BF"], "bpo_fac.csv"),
    (["EN"], "mcbc.csv"),
    (["BG", "BK", "CZ"], "behr.csv")
    ]

HEADINGS = [
    "Doc. no.",
    "Pers.No.",
    "Date",
    "WBS Elem.",
    "A/A type",
    "Oper./Act.",
    "SubSvcTech",
    "Process",
    "Dlvry Mode",
    "Coverage",
    "Attribute",
    "Hours",
    "OprShrtTxt",
    "Cust Fld 1",
    "Cust Fld 2",
    "Cust Fld 3",
    "Inv Cd",
    "Capability",
    "Proj Task",
    "New Rem Wk"
    ]


WKDAY_MAP = {
    "BF": {
        "FA": "zzz-3660.R01.BFAA",
        "ELSE": "zzz-3600.R01.BHOS"
        },
    "EN": {
        "FA": "zzz-2115.R01.BFAA",
        "ELSE": "zzz-2115.R01.BHOS"
    },
    "BG": {
        "FA": "zzz-3662.R01.BFAA",
        "ELSE": "zzz-3662.R01.BHOS"
    },
    "BK": {
        "FA": "zzz-3662.R01.BFAA",
        "ELSE": "zzz-3662.R01.BHOS"
    },
    "CZ": {
        "FA": "zzz-3662.R01.BFAA",
        "ELSE": "zzz-3662.R01.BHOS"
    }
}

DAYTYPE_MAP = {
    'HOLIS': "ZZZ-9999.INT.ABSNCE",
    'SICKD': "ZZZ-9999.INT.ABSNCE",
    'PUABS': "ZZZ-9999.INT.ABSNCE",
    'RETRN': "ZZZ-9999.INT.ABSNCE",
    'ROVER': "ZZZ-9999.INT.ABSNCE",
    'DAYOD': "ZZZ-9999.INT.ABSNCE",
    'SPECI': "ZZZ-9006.INT.OTHER",
    'OTHER': "ZZZ-9006.INT.OTHER",
    'SATUR': "zzz-1537.R01.BHOS",
    'WKHOM': "zzz-1537.R01.BHOS",
    'TRAIN': "ZZZ-9999.INT.ATTEND",
    'PUWRK': "ZZZ-9999.INT.ATTEND",
}

def catw_code(user, daytype):
    '''Calculates the CATW Code for the employee using a specific
    daytype.'''
    if daytype == "WKDAY":
        if user.process == "FA":
            return WKDAY_MAP[user.market]["FA"]
        else:
            return WKDAY_MAP[user.market]["ELSE"]
    return DAYTYPE_MAP[daytype]

def blankrow(user, year, month, day):
    '''Returns what the blank row (empty day) looks like in the CATW
    report.'''
    # skip the weekends
    if datetime.date(year=int(year),
                     month=int(month),
                     day=int(day)).weekday() in [5,6]:
        return []
    return [
        "", user.user_id, "%s/%s/%s" % (month, day, year),
        catw_code(user, "WKDAY"), "400",
        # the rest are empty except for the time.
        "", "","", "", "", "%.2f" % user.shiftlength_as_float(),
        "","","","","","","",""
        ]

def realrow(user, year, month, day, entry):
    '''Returns a real row for the user.'''
    return [
        "", user.user_id, "%s/%s/%s" % (month, day, year),
        catw_code(user, entry.daytype), "400",
        # the rest are empty except for the time.
        "", "","", "", "", "%.2f" % entry.round_down() \
        if entry.daytype != "HOLIS" else user.shiftlength_as_float(),
        "","","","","","","",""
        ]

def report_for_account(choice_list, year, month):
    '''
    Writes out the report to disk.
    '''

    accs, filename = choice_list

    csvout = csv.writer(open(filename, "wb"))
    csvout.writerow(HEADINGS)

    users = Tbluser.objects.filter(market__in=accs)
    entries = TrackingEntry.objects.select_related("user").filter(
        user__market__in=accs,
        entry_date__year=year,
        entry_date__month=month
        )

    # we generate the map using blank dicts since we need to use the
    # id of the employee (who may not have any entries this month).
    entry_map = {user.id: {} for user in users}
    for entry in entries:
        if entry.is_linked():
            continue
        if entry_map.get(entry.user.id):
            entry_map[entry.user.id][str(entry.entry_date)] = entry
        else:
            entry_map[entry.user.id] = {
                str(entry.entry_date): entry
                }

    # get a list of valid day numbers for the month we're creating
    # the report for. Prefix all single-digit digits with a leading
    # "0" so they format well for the date strings.
    days_this_month = [day if day > 9 else "0%d" % day for day in filter(
            lambda x: x > 0,
            list(calendar.Calendar().itermonthdays(year, month))
            )]
    # Prefix the month digit with a leading "0"
    months = month if month > 9 else "0%d" % month

    for user in users:
        for day in days_this_month:
            entry = entry_map[user.id].get("%s-%s-%s" % (year, months, day))
            if entry:
                csvout.writerow(realrow(user, year, months, day, entry))
            else:
                csvout.writerow(blankrow(user, year, months, day))

class Command(BaseCommand):
    '''Implementation of a Django command.'''
    option_list = BaseCommand.option_list + (
        make_option('--year',
                    action='store',
                    default=datetime.datetime.now().year,
                    dest='year',
                    help='The year to run the report for.'),
        make_option('--month',
                    action='store',
                    default=datetime.datetime.now().month,
                    dest='month',
                    help='The month to run the report for.'),
        )

    def handle(self, *args, **options):
        '''This is what gets invoked from manage.py catw_report.

        You may supply this command with a list of short market codes
        doing this will generate a CATW report for each of those markets.
        The files will be generated locally.'''
        year = int(options.get('year'))
        month = int(options.get('month'))
        for choice_list in CHOICES:
            report_for_account(choice_list, year, month)
