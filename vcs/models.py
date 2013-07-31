from collections import defaultdict, OrderedDict
from datetime import datetime
from decimal import Decimal

from django.db import models
from django.core.cache import cache

from timetracker.utils.datemaps import ABSENT_CHOICES, group_for_team


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
    def filterforyearmonth(teams, year=None, month=None):
        # to prevent circular imports
        from timetracker.tracker.models import TrackingEntry
        if year is None:
            year = datetime.today().year
        if month is None:
            month = datetime.today().month

        invalidset = defaultdict(list)
        [invalidset[entry.user.id].append(entry.id)
         for entry in TrackingEntry.objects.filter(
                daytype__in=["PUABS", "DAYOD"]
         ).select_related("user")]

        def invalid(entry):
            return entry.id in invalidset[entry.user.id]

        return ActivityEntry.objects.filter(
            user__market__in=teams,
            creation_date__year=year,
            creation_date__month=month
        ).select_related("activity", "user"), invalid

    @staticmethod
    def costbucket_count(teams, year=None, month=None):
        entries, _ = ActivityEntry.filterforyearmonth(teams, year, month)
        costbuckets = defaultdict(int)
        for entry in entries:
            costbuckets[entry.activity.costbucket] += 1
        return costbuckets

    @staticmethod
    def utilization_calculation(teams, year=None, month=None):
        if year is None:
            year = datetime.today().year
        if month is None:
            month = datetime.today().month

        cached_result = cache.get("utilization:%s%s%s" % (''.join(teams), year, month))
        if cached_result:
            return cached_result

        # prevent circular imports
        from timetracker.utils.calendar_utils import working_days
        from timetracker.tracker.models import Tbluser, TrackingEntry

        entries, invalid = ActivityEntry.filterforyearmonth(teams, year, month)
        effi, util = (0, 0)
        losses = TrackingEntry.objects.filter(user__market__in=teams,
                                              daytype=["PUABS", "DAYOD", "HOLIS"],
                                              entry_date__year=year,
                                              # 460 is a single
                                              # industrial engineering
                                              # FTE in Minutes.
                                              entry_date__month=month).count() * 460
        for entry in entries:
            if invalid(entry):
                continue
            time = entry.amount * entry.activity.time
            if entry.activity.group != "ALL":
                util += time
            else:
                losses += time
            effi += time

        available_time = (Tbluser.available_minutes(teams) * len(working_days(year, month)))
        utilization_percent = (100 * (Decimal(util) / Decimal(available_time)))
        efficiency_percent = (100 * (Decimal(util) / (Decimal(available_time) - Decimal(losses))))
        availability_percent = (100 * (Decimal(available_time) - Decimal(losses)) / Decimal(available_time))

        res = {
            "util": {
                "percent": utilization_percent,
                "target": 65
            },
            "effi": {
                "percent": efficiency_percent,
                "target": 85
            },
            "avai": {
                "percent": availability_percent,
                "target": 80
            }
        }
        cache.set("utilization:%s%s%s" % (''.join(teams), year, month), res)
        return res

    @staticmethod
    def utilization_last_12_months(teams, year=None, month=None):
        from timetracker.utils.calendar_utils import last12months

        if year is None:
            year = datetime.today().year
        if month is None:
            month = datetime.today().month

        dates = last12months(year, month)
        utilization = OrderedDict()
        for date in dates:
            utilization[date] = ActivityEntry.utilization_calculation(
                teams, date.year, date.month
            )
        return utilization, dates

    @staticmethod
    def activity_volumes(teams, year=None, month=None, activity=None):
        if year is None:
            year = datetime.today().year
        if month is None:
            month = datetime.today().month

        cached_result = cache.get("activity_volumes:%s%s%s%s" % (''.join(teams), year, month, activity))
        if cached_result:
            return int(cached_result)

        if activity is None:
            return 0

        res = sum(map(lambda e: e.amount, ActivityEntry.objects.filter(
            user__market__in=teams,
            activity=activity,
            creation_date__year=year,
            creation_date__month=month
        )))
        cache.set("activity_volumes:%s%s%s%s" % (''.join(teams), year, month, activity), str(res))
        return res

    @staticmethod
    def activity_volumes_last_12_months(teams, year=None, month=None, activity=None):
        from timetracker.utils.calendar_utils import last12months
        if activity is None:
            return [0 for _ in range(12)]

        if year is None:
            year = datetime.today().year
        if month is None:
            month = datetime.today().month

        dates = last12months(year, month)
        return (
            ActivityEntry.activity_volumes(teams, date.year, date.month, activity) \
            for date in dates
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        cache.delete(
            "activity_volumes:%s%s%s%s" % (''.join(group_for_team(self.user.market)),
                                           self.creation_date.year,
                                           self.creation_date.month,
                                           self.activity.id)
        )
        cache.delete(
            "utilization:%s%s%s" % (''.join(group_for_team(self.user.market)),
                                    self.creation_date.year,
                                    self.creation_date.month)
        )
        super(ActivityEntry, self).save(*args, **kwargs)

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
