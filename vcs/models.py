from django.db import models

class Activity(models.Model):
    group = models.CharField(max_length=4)
    grouptype = models.TextField()
    groupdetail = models.TextField()
    details = models.TextField()
    disabled = models.BooleanField()
    time = models.DecimalField(decimal_places=2, max_digits=10)
    unique_together = (("group", "grouptype", "disabled", "time"),)

class ActivityEntry(models.Model):
    from timetracker.tracker.models import Tbluser
    user = models.ManyToManyField(
        Tbluser,
        related_name="user_foreign"
    )
    activity = models.ManyToManyField(
        Activity,
        related_name="activity_foreign"
    )
    amount = models.BigIntegerField()

    def time(self):
        return self.activity.time * self.amount
