import datetime as dt

from django.core.cache import cache
from django.db import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template

from timetracker.utils.datemaps import DAYTYPE_CHOICES, round_down
from timetracker.loggers import debug_log, suspicious_log, cache_log


try:
    # The modules which provide these functions should be provided for by
    # the setup environment, this is due to the fact that some notifications
    # may include business-specific details, we can override by simply incl-
    # uding a local notifications.py in this directory with the required fu-
    # nctions we need.
    from timetracker.tracker.notifications import (
        send_overtime_notification, send_pending_overtime_notification,
        send_undertime_notification
        )
# pragma: no cover
except ImportError as e:
    debug_log.debug(str(e))
    #pylint: disable=W0613
    def send_overtime_notification(*args, **kwargs):
        '''Not implemented'''
        debug_log.debug("default implementation of send_overtime_notification.")
    def send_pending_overtime_notification(*args, **kwargs):
        '''Not implemented'''
    def send_undertime_notification(*args, **kwargs):
        '''Not implemented'''


class TrackingEntry(models.Model):

    '''Model which is used to enter working logs into the database.

    A tracking entry consists of several fields:-

    1) Entry date: The date that the working log happened.
    2) Start Time: The start time of the working day.
    3) End Time: The end time of the working day.
    4) Breaks: Any breaks taken during that day.
    5) Day Type: The type of working log.

    Again, the TrackingEntry model is a core component of the time tracking
    application. It directly links users with the time-spent at work and the
    the type of day that was.
    '''

    user = models.ForeignKey("Tbluser", related_name="user_tracking")
    link = models.ForeignKey("self", related_name="linked_entry",
                             null=True, blank=True, on_delete=models.SET_NULL)
    entry_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    breaks = models.TimeField()
    daytype = models.CharField(choices=DAYTYPE_CHOICES,
                               max_length=5)

    comments = models.TextField(blank=True)

    class Meta:
        '''
        Metaclass gives access to additional options
        '''
        verbose_name = 'Daily Tracking Log'
        verbose_name_plural = 'Daily Tracking Logs'
        unique_together = ('user', 'entry_date')
        ordering = ['user']

    def save(self, *args, **kwargs):
        super(TrackingEntry, self).save(*args, **kwargs)
        self.full_clean()
        self.invalidate_caches()
        if self.daytype == "WKDAY" and \
                self.entry_date.isoweekday() in [6, 7]:
            self.daytype = "SATUR"
            super(TrackingEntry, self).save(*args, **kwargs)

    def __unicode__(self):

        '''
        Method to display entry in admin

        :rtype: :class:`string`
        '''

        date = '/'.join(
            map(unicode,
                [self.entry_date.year,
                 self.entry_date.month,
                 self.entry_date.day
                 ])
            )

        return unicode(self.user) + ' - ' + date

    def invalidate_caches(self):
        if self.daytype in ["DAYOD", "HOLIS"]:
            cache.delete(
                "holidaytablerow%s%s" %
                (self.user.id, self.entry_date.year)
            )
        cache.delete("holidayfields:%s%s%s" % (
            self.user.id, self.entry_date.year, self.entry_date.month)
        )
        cache.delete("tracking_entries:%s%s%s" % (
            self.user.id, self.entry_date.year, self.entry_date.month)
        )
        cache.delete("numdaytype:%s%s%s" % (
            self.user.id, self.entry_date.year, self.daytype)
        )
        cache.delete("holidaybalance:%s%s" % (self.user.id, self.entry_date.year))
        cache.delete("yearview:%s%s" % (self.user.id, self.entry_date.year))
        cache.delete("overtime_view:%s%s" % (self.user.id, self.entry_date.year))

    @staticmethod
    def headings():
        '''Describes this class as if it were a CSV heading bar.'''
        #pragma: no cover
        return [
            "User", "Entry Date", "Start Time", "End Time", "Breaks",
            "Daytype", "Comments"
            ]

    @property
    def worklength(self):
        '''Returns the working portion of this tracking entry'''
        td = dt.timedelta(hours=self.end_time.hour,
                          minutes=self.end_time.minute)
        td += self.normalized_break()
        return td

    def user_can_see(self, user):
        '''Method checks to see if the user passed-in is privvy to view
        the details of this TrackingEntry.

        :param user: A Tbluser instance.
        :return: A boolean indicating whether or not the user is
                 allowed to view this entry.
        '''
        from timetracker.tracker.models import Tbluser
        try:
            user.get_subordinates().get(id=self.user.id)
            return True
        except Tbluser.DoesNotExist:
            suspicious_log.critical(
                "An accept/edit check was made by %s for an entry which " \
                % self.user.name() + \
                "is for a person outside their team"
            )
            return False

    def is_linked(self):
        '''Checks whether this particular entry is a linked entry.'''
        return self.daytype == "LINKD" or self.link

    def unlink(self):
        '''If this current entry is linked, then we will unlink the entry and
        set the target link to a regular working day.
        '''
        if self.link:
            if self.link.daytype == "LINKD" and \
               len(TrackingEntry.objects.filter(link=self.link)) == 1:
                self.link.delete()
            else:
                self.link = None
                self.save()

    def breaktime(self):
        '''Returns the breaks entry of this tracking entry.'''
        return (dt.timedelta(hours=self.breaks.hour,
                             minutes=self.breaks.minute).seconds / 60.0) / 60.0

    def display_as_csv(self):
        '''Returns the tracking entry as a CSV row.'''
        return [
            self.user.name(), self.entry_date, self.start_time,
            self.end_time, self.breaks, self.get_daytype_display(),
            self.comments
            ]

    def threshold(self):
        '''Returns the threshold for the associated user.'''
        return settings.OT_THRESHOLDS.get(
            self.user.market,
            settings.DEFAULT_OT_THRESHOLD
            )

    def totalhours(self):
        '''Total hours calculated for this tracking entry'''
        td = dt.timedelta(hours=self.end_time.hour,
                          minutes=self.end_time.minute)
        td -= dt.timedelta(hours=self.start_time.hour,
                           minutes=self.start_time.minute)
        td += dt.timedelta(hours=self.breaks.hour,
                           minutes=self.breaks.minute)
        debug_log.debug(str((td.seconds / 60.0) / 60.0))
        return ((td.seconds / 60.0) / 60.0)

    def nearest_half(self):
        '''Rounds the time to the nearest half hour.'''
        return nearest_half(self.totalhours())

    def round_down(self):
        '''Rounds the time to the nearest half hour downwards.'''
        return round_down(self.totalhours())

    def normalized_break(self):
        '''Returns the shorter of breaklengths between the users actual break
        length and the one for this entry.'''
        breaklength = dt.timedelta(hours=self.breaks.hour,
                                   minutes=self.breaks.minute)
        breaklength_reg = dt.timedelta(hours=self.user.breaklength.hour,
                                       minutes=self.user.breaklength.minute)
        if breaklength.seconds > breaklength_reg.seconds:
            debug_log.debug("Returning regular break.")
            return breaklength_reg
        else:
            debug_log.debug("Returning actual break.")
            return breaklength

    def total_working_time(self):
        '''Total working time returns the actual working time of an
        entry, ignoring breaks taken over the regular amount.'''
        td = dt.timedelta(hours=self.end_time.hour,
                          minutes=self.end_time.minute)
        td -= dt.timedelta(hours=self.start_time.hour,
                           minutes=self.start_time.minute)
        td += self.normalized_break()
        return ((td.seconds / 60.0) / 60.0)

    def approval_required(self):
        '''Returns whether this entry is needing approval in order to be
        processed.'''
        return self.is_overtime() \
            or self.is_undertime() \
            or self.daytype == "PENDI"

    def is_overtime(self):
        '''Determines whether this tracking entry is overtime.'''
        if self.daytype == "WKDAY":
            return self.time_difference() >= self.threshold()
        else:
            return False

    def is_undertime(self):
        '''Determines whether this tracking entry is undertime.'''
        if self.daytype == "WKDAY":
            return self.time_difference() <= -self.threshold()
        else:
            return False

    def overtime_class(self):
        '''Returns a string for the CSS class to use when using this entry in
        the context of over/undertime.'''
        if self.is_overtime():
            return 'OVERTIME'
        elif self.is_undertime():
            return 'UNDERTIME'
        elif self.daytype == "ROVER":
            return "ROVER"
        else:
            return 'OK'

    def time_difference(self):
        '''Calculates the difference between this tracking entry and the user's
        shiftlength'''
        value = round_down(self.total_working_time()) - \
                self.user.shiftlength_as_float()
        debug_log.debug("Time difference:" + str(value))
        return value

    def sending_undertime(self):
        '''Returns if we are sending undertime for this entry.'''
        return settings.UNDER_TIME_ENABLED.get(self.user.market)

    def pending(self):
        '''Checks to see if the entry the PendingApproval object associated
        with this exists and is still open.'''
        from timetracker.overtime.models  import PendingApproval
        return len(PendingApproval.objects.filter(closed=False, entry=self)) > 0

    def create_approval_request(self):
        '''create_approval_request will take this entry and create a
        PendingApproval entry pointing back to this one.'''
        # to avoid circular import dependencies
        from timetracker.overtime.models  import PendingApproval

        if self.pending():
            return
        if not self.overtime_notification_check() and \
           not self.undertime_notification_check() and \
           not self.daytype == "PENDI":
            return
        approval_request = PendingApproval(
            entry=self,
            approver=self.user.get_administrator()
        )
        approval_request.save()
        approval_request.inform_manager()

    def overtime_notification_check(self):
        '''Checks if this entry is overtime or not for the purposes of
        sending notifications.'''
        return self.daytype == "WKDAY" and self.is_overtime() or \
            self.daytype in ["PUWRK", "SATUR", "LINKD"]

    def undertime_notification_check(self):
        '''Checks if this entry is undertime or not for the puporses of
        sending notifications.'''
        return self.is_undertime() and self.sending_undertime()

    def send_notifications(self):
        '''Send the associated notifications for this tracking entry.
        For example, if this entry is an overtime entry, it will generate and
        send out the e-mails as per the rules.'''
        debug_log.debug("Send Overtime?:" + \
                        str(self.overtime_notification_check())
        )
        if self.daytype == "HOLIS":
            return self.holiday_approval_notification()
        if self.overtime_notification_check():
            debug_log.debug("Overtime created: " + self.user.name())
            send_overtime_notification(self)
            return
        if self.undertime_notification_check():
            send_undertime_notification(self)
            return

    def holiday_approval_notification(self):
        '''Send the associated holiday approval for this entry.'''
        templ = get_template("emails/holiday_approved.dhtml")
        ctx = Context({
            "entry_date": str(self.entry_date)
            })
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = templ.render(ctx)
        email.to = [self.user.user_id]
        email.cc = self.user.get_manager_email()
        email.subject = "Holiday Request: Approved."
        email.send()
