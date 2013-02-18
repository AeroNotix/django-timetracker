from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import *

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for i in TrackingEntry.objects.filter(user_id=1):
            i.send_notifications()
