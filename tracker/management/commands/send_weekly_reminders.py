from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import Tbluser

class Command(BaseCommand):
    help = \
        'Sends a reminder of the current balance levels to all accounts ' \
        'in the argument list'

    def handle(self, *args, **options):
        for user in Tbluser.objects.filter(market__in=args):
            user.send_weekly_reminder()
