#pylint: disable=E1101,W0232,W0141,E1103,E1002,W0232,R0201,R0903,R0904,C0302
#pylint: disable=C0103
'''The overtime application encapsulates some common functionality
with the overtime approval queues in the timetracker application.
'''
import datetime

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from timetracker.tracker.models import TrackingEntry, Tbluser


class PendingApproval(models.Model):
    '''PendingApproval is the model with which we store
    Overtime/Undertime and Work at weekend approval requests.

    When an agent is required to work under these specific conditions
    we must be able to track this and have a proper approval
    chain. The agent first creates their entry using the normal
    methods and an approval request is generated. This approval
    request is then available for their immediate manager to approve
    or deny it.

    Approving a request means that the agent will then receive the
    normal follow-up e-mails and the notification plugin functions
    will be ran.

    Denying a request simply deletes the entry and informs the agent
    that the request was not successful.

    '''
    created_on = models.DateField(
        auto_now_add=True
    )
    closed = models.BooleanField()
    closed_on = models.DateField(null=True, blank=True)
    entry = models.ForeignKey(
        TrackingEntry
    )
    approver = models.ForeignKey(
        Tbluser,
        limit_choices_to={
            "user_type__in": ["SUPER", "ADMIN"]
        }
    )

    def close(self, status):
        '''Close, as the name implies, closes this PendingApproval request.

        When we close the entry we make a timestamp for when it was
        closed and send the appropriate follow-up e-mails.

        If the entry is approved, status should be True and this will
        keep the entry in the system and generate all the associated
        forms.

        If the entry is denied, then it will delete the associated
        entry and any link days which are associated with *that* entry.

        :param status: Boolean indicating whether this entry was approved.
        '''
        if self.closed:
            return
        self.closed = True
        self.closed_on = datetime.datetime.now()
        self.save()
        if status:
            self.approved()
        else:
            self.denied()

    def approved(self):
        '''approved fires off the notifications associated with this entry.'''
        self.entry.send_notifications()

    def denied(self):
        '''denied will inform the user that their request was not successful.'''
        message = \
                  "Hi,\n\n" \
                  "Your request for overtime on %s was denied.\n\n" \
                  "Kind Regards,\n" \
                  "Timetracking Team"
        message = message % str(self.entry.entry_date)
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = message
        email.to = [self.entry.user.user_id]
        email.subject = "Request for Overtime: Denied."
        email.send()
        if self.entry.is_linked():
            self.entry.link.delete()
        self.entry.delete()
        self.delete()

    def __unicode__(self):
        return u'%s - %s' % (self.entry.entry_date, self.entry.user.name())

    def inform_manager(self):
        '''When we create a PendingApproval we can inform the manager that a
        new entry was created.

        '''

        if not self.entry.approval_required():
            return

        if not settings.SENDING_APPROVAL.get(self.approver.market):
            return

        message = \
                  "Hi,\n\n" \
                  "An approval request from %s was just created for %s." \
                  "\n\n" \
                  "You can approve, edit or deny this request in the " \
                  "following link: %s%s\n\n" \
                  "Kind Regards,\n" \
                  "Timetracking Team"
        message = message % (
            self.entry.user.name(),
            str(self.entry.entry_date),
            settings.DOMAIN_NAME,
            reverse(
                "timetracker.overtime.views.accept_edit",
                kwargs={"entry": self.entry.id},
            )[1:] # because it has the leading slash
        )
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = message
        email.to = self.entry.user.get_manager_email()
        email.subject = "Request for Overtime: %s" % self.entry.user.name()
        email.send()
