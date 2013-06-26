import datetime

from django.db import models

from timetracker.tracker.models import TrackingEntry, Tbluser


class PendingApproval(models.Model):

    created_on = models.DateField(
        auto_now_add=True
    )
    closed = models.BooleanField()
    closed_on = models.DateField(null=True)
    entry = models.ForeignKey(
        TrackingEntry
    )
    approver = models.ForeignKey(
        Tbluser,
        limit_choices_to={
            "user_type__in": ["SUPER", "ADMIN"]
        }
    )

    def close(self):
        self.closed = True
        self.closed_on = datetime.datetime.now()
        self.save()
