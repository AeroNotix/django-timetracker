from django.db import models

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

    class Meta:
        verbose_name_plural = "Activity Entries"