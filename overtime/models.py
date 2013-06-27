import datetime

from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse

from timetracker.tracker.models import TrackingEntry, Tbluser


class PendingApproval(models.Model):

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
        self.entry.send_notifications()

    def denied(self):
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

    def __unicode__(self):
        return u'%s - %s' % (self.entry.entry_date, self.entry.user.name())

    def inform_manager(self):
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
