from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import *

from django.core import mail
connection = mail.get_connection()

class Command(BaseCommand):
    help = 'Sends notifications of overtime balances to the all those ' \
           'who have balances over zero hours.'

    def handle(self, *args, **options):
        messages = filter(lambda x: x != None,
                          [user.send_pending_overtime_notification(send=False)
                           for user in Tbluser.objects.filter(disabled=False)])
        connection.send_messages(messages)
