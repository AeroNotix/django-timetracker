'''Generates a holiday chart for a year'''

import datetime
import numpy as np
import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import TrackingEntry

def gendates(year):
    '''Generates the dates for a given year.'''
    m = {}
    d = datetime.date(year, 1, 1)
    td = datetime.timedelta(days=1)
    while d.year == year:
        m[d] = 0
        d += td
    return m

class Command(BaseCommand):
    '''Django command.'''
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        '''Implementation.'''
        year = args[0]
        totals = gendates(int(year))
        for date_entry in TrackingEntry.objects.filter(entry_date__year=year, daytype="HOLIS"):
            totals[date_entry.entry_date] += 1

        total_nums = [item[1] for item in totals.items()]

        N = len(total_nums)
        ind = np.arange(N)
        width = 0.35

        fig = plt.figure()
        ax = fig.add_subplot(111)
        rects1 = ax.bar(ind, total_nums, width, color='r')
        fig.savefig("/home/aero/fig1.png")
