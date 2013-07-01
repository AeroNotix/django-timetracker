'''
Simple module to aid in command-line debugging of notification related issues.
'''

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import EmailMessage

from timetracker.overtime.models import PendingApproval, Tbluser

def send_approval_digest(market):
    approvals = PendingApproval.objects.filter(closed=False, approver__market=market)
    if not len(approvals):
        return
        if len({entry.approver for entry in approvals}) > 1:
            error_log.critical(
                "Cannot send e-mails as a clear approval chain cannot be established."
            )
        return
            
    message = "Hi,\n\n" \
              "You have %d approvals pending in the timetracker." \
              "\n\n" \
              "Kind Regards,\n" \
              "Timetracker team"

    message = message % len(approvals)

    email = EmailMessage(from_email='timetracker@unmonitored.com')
    email.body = message
    email.to = approvals[0].entry.user.get_manager_email()
    email.subject = "Pending Approvals in the Timetracker."
    email.send()


class Command(BaseCommand):

    def handle(self, *args, **options):
        for market in Tbluser.MARKET_CHOICES:
            if settings.SENDING_APPROVAL_DIGESTS.get(market[0]):
                send_approval_digest(market[0])
            
