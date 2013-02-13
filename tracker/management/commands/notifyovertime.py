from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import *

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for user in Tbluser.objects.filter(id=1):
            user.send_pending_overtime_notification()
            break
