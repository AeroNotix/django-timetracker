'''
Simple module to aid in command-line debugging of notification related issues.
'''

from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import TrackingEntry

class Command(BaseCommand):
    '''Django command'''
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        '''implementation'''
        for i in TrackingEntry.objects.filter(user_id=331):
            i.send_notifications()
