'''This enables a django command for sending a total to an individual about
there overtime balances.'''

from django.core.management.base import BaseCommand, CommandError
from timetracker.tracker.models import Tbluser

from django.core import mail
connection = mail.get_connection()

class Command(BaseCommand):
    '''Implementation of a Django command.'''
    help = 'Sends notifications of overtime balances to the all those ' \
           'who have balances over zero hours.'

    def handle(self, *args, **options):
        '''Main entry point'''
        messages = filter(lambda x: x != None,
                          [user.send_pending_overtime_notification(send=False)
                           for user in Tbluser.objects.filter(disabled=False)])
        connection.send_messages(messages)
