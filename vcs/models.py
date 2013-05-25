from django.db import models

class Activity(models.Model):
    group = models.CharField(max_length=4)
    grouptype = models.TextField()
    groupdetail = models.TextField()
    details = models.TextField()
    disabled = models.BooleanField()
    time = models.DecimalField(decimal_places=2, max_digits=10)
    unique_together = (("group", "grouptype", "disabled", "time"),)

    def __unicode__(self):
        return u"%s - %s - %s - %s" % (self.group,
                                       self.grouptype,
                                       self.groupdetail,
                                       self.details)

    class Meta:
        verbose_name_plural = "Activities"

class ActivityEntry(models.Model):
    user = models.ForeignKey(
        'tracker.Tbluser',
        related_name="user_foreign"
    )
    activity = models.ForeignKey(
        Activity,
        related_name="activity_foreign"
    )
    amount = models.BigIntegerField()

    def time(self):
        return self.activity.time * self.amount

    class Meta:
        verbose_name_plural = "Activity Entries"
