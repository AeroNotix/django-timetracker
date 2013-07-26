from collections import defaultdict
from datetime import datetime

from django.db import models

COSTBUCKETS = (
    ('PVA', 'Processing Value Add'),
    ('PVE', 'Processing Value Enabling'),
    ('PNVE', 'Processing Non Value Add'),
    ('QAPP', 'Quality Appresial'),
    ('QPR', 'Quality Prevention'),
    ('QIF', 'Quality Internal Failure'),
    ('QIFPQ', 'Quality Internal Failure Process Quality'),
    ('QIFPI', 'Quality Internal Failure Poor Input Quality'),
    ('QIFRC', 'Quality Internal Failure Rework Cost'),
    ('QEF', 'Quality External Failure'),
    ('QEFQR', 'Quality External Failure Query Resolution'),
    ('QEFER', 'Quality External Failure External Rework'),
    ('QEFCE', 'Quality External Failure Customer Escalations'),
    ('COUTT', 'Cost of Under Utilization Non Transactional Time'),
    ('COUUL', 'Cost of Under Utilization Unavoidable Loss'),
    ('COUAL', 'Cost of Under Utilization Avoidable Loss'),
)


class Activity(models.Model):
    """Activity encapsulates the idea of a single task for Industrial
    Engineering purposes.

    Group: This is the concatenation of the account and the process
    this is used to find which employees a particular activity is
    aimed at.

    Group Type: This is the category in which a particular activity
    resides

    Group Detail: This is similar to a sub-category, this gives a lot
    more details on what the Activity is.

    Details: This shows what the volume represents when you create a
    related ActivityEntry.

    Disabled: Currently unused.

    Time: the time factor for this Activity, how long it takes to
    process.
    """

    group = models.CharField(max_length=4)
    grouptype = models.CharField(max_length=100)
    groupdetail = models.CharField(max_length=100)
    details = models.CharField(max_length=256)
    disabled = models.BooleanField()
    time = models.DecimalField(decimal_places=2, max_digits=10)
    costbucket = models.CharField(max_length=5, choices=COSTBUCKETS)

    def __unicode__(self): # pragma: no cover
        return u"%s - %s - %s - %s" % (self.group,
                                       self.grouptype,
                                       self.groupdetail,
                                       self.details)

    class Meta:
        unique_together = (("group", "grouptype", "groupdetail", "time"),)
        verbose_name_plural = "Activities"

class ActivityEntry(models.Model):
    """ActivityEntry allows us to join together a single Activity along
    with the user, amount and creation date of when the Activity took
    place.

    User: This is the user associated with this particular
    ActivityEntry.

    Activity: An instance of the Activity this ActivityEntry is linked
    to.

    Amount: an integer representing how many of that particular
    Activity was completed.

    Creation Date: The date that this ActivityEntry was created.
    """

    user = models.ForeignKey(
        'tracker.Tbluser',
        related_name="user_foreign"
    )
    activity = models.ForeignKey(
        Activity,
        related_name="activity_foreign"
    )
    amount = models.BigIntegerField()
    creation_date = models.DateField()

    def time(self): # pragma: no cover
        return self.activity.time * self.amount

    def __unicode__(self): # pragma: no cover
        return u'%s - %s - %d' % (self.user, self.activity, self.time())

    @staticmethod
    def costbucket_count(teams, year=None, month=None):
        if year is None:
            year = datetime.today().year
        if month is None:
            month = datetime.today().month
        costbuckets = defaultdict(int)
        entries = ActivityEntry.objects.filter(
            user__market__in=teams,
            creation_date__year=year,
            creation_date__month=month
        ).select_related("activity")
        for entry in entries:
            costbuckets[entry.activity.costbucket] += 1
        return costbuckets

    class Meta:
        verbose_name_plural = "Activity Entries"

class Offset(models.Model):
    amount = models.IntegerField()
    costbucket = models.CharField(max_length=5, choices=COSTBUCKETS)

    def __unicode__(self): # pragma: no cover
        return u'%d%% - %s' % (self.amount, self.get_costbucket_display())

class ActivityOffset(models.Model):
    activity = models.ForeignKey(Activity)
    offset = models.ManyToManyField(Offset)
