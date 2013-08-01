#pylint: disable=E1101,W0232,W0141,E1103,E1002,W0232,R0201,R0903,R0904,C0302
#pylint: disable=C0103
'''The overtime application encapsulates some common functionality
with the overtime approval queues in the timetracker application.
'''
import datetime

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
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
    tl_approved = models.BooleanField()

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
        if self.closed: # pragma: no cover
            return
        self.closed = True
        self.closed_on = datetime.datetime.now()
        self.save()
        if status:
            if self.entry.daytype == "PENDI": # pragma: no cover
                self.entry.daytype = "HOLIS"
                self.entry.save()
            self.approved()
        else:
            self.denied()

    def tl_close(self, status):
        '''Performs a 'soft close' on the PendingApproval entry by simply
        marking the tl_approved as True. This allows us to know that
        an entry can be approved by a one-up manager.
        '''
        if self.closed: # pragma: no cover
            return
        if status:
            self.tl_approved = True
            self.save()
        else:
            self.denied()

    def approved(self):
        '''approved fires off the notifications associated with this entry.'''
        self.entry.send_notifications()

    def denied(self):
        '''denied will inform the user that their request was not successful.'''
        tmpl = get_template("emails/denied.dhtml")
        ctx = Context({
            "entry_date": str(self.entry.entry_date),
            "daytype": self.entry.daytype,
        })
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = tmpl.render(ctx)
        email.to = [self.entry.user.user_id]
        email.subject = "Request for Overtime: Denied."
        email.send()
        if self.entry.is_linked(): # pragma: no cover
            self.entry.link.unlink()
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

        if settings.SENDING_APPROVAL_MANAGERS.get(self.approver.market):
            managers = self.entry.user.get_manager_email()
        else:
            managers = []

        if settings.SENDING_APPROVAL_TL.get(self.approver.market):
            tls = self.entry.user.get_tl_email()
        else:
            tls = []

        recipients = managers + tls
        if len(recipients) == 0:
            return

        tmpl = get_template("emails/inform_manager.dhtml")
        ctx = Context({
            "username": self.entry.user.name(),
            "entry_date": str(self.entry.entry_date),
            "domain": settings.DOMAIN_NAME,
            "daytype": self.entry.daytype,
            "rest": reverse(
                "timetracker.overtime.views.accept_edit",
                kwargs={"entry": self.entry.id},
            )[1:] # because it has the leading slash
        })
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = tmpl.render(ctx)
        email.to = recipients
        email.subject = "Request for Overtime: %s" % self.entry.user.name()
        email.send()

    def is_holiday_request(self):
        '''checks whether this entry is a holiday entry or not.'''
        return self.entry.daytype == "PENDI"
