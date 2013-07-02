#pylint: disable=E1101,W0232,W0141,E1103,E1002,W0232,R0201,R0903,R0904,C0302
#pylint: disable=C0103

'''Definition of the models used in the timetracker app

    .. moduleauthor:: Aaron France <aaron.france@hp.com>

    :platform: All
    :synopsis: Module which contains view functions that are mapped from urls
'''

import datetime as dt

from operator import add

from django.db import models
from django.forms import ModelForm
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template

from timetracker.loggers import debug_log, suspicious_log

try:
    NUM_WORKING_DAYS = settings.NUM_WORKING_DAYS
except AttributeError:
    # usual working day amount
    NUM_WORKING_DAYS = 5

from timetracker.utils.datemaps import (
    WORKING_CHOICES, DAYTYPE_CHOICES, float_to_time, datetime_to_timestring,
    MONTH_MAP, generate_year_box, nearest_half, round_down
    )

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


class Tbluser(models.Model):

    '''Models the user table and provides the admin interface with the
    niceties it needs.

    This model is the central pillar to this entire application.

    The permissions for a user is determined in the view functions,
    not in a table this is a design choice because there is only a
    minimal set of things to have permissions *over*, so it would be
    overkill to take full advantage of the MVC pattern.

    User\n
    The most general and base type of a User is the *RUSER*, which is
    shorthand (and what actually gets stored in the database) for
    Regular User. A regular user will only be able to access a
    specific section of the site.

    Team Leader\n
    The second type of User is the *TEAML*, this user has very similar
    level access as the administrator type but has only a limited
    subset of their access rights. They cannot have a team of their
    own, but view the team their manager is assigned. They cannot view
    and/or change job codes, but they can create new users with all
    the *other* information that they need. They can
    view/create/add/change holidays of themselves and the users that
    are assigned to their manager.

    Administrator\n
    The third type of User is the Administrator/*ADMIN*. They have
    full access to all functions of the app. They can
    view/create/change/delete members of their team. They can
    view/create/add/change holidays of all members of their team and
    themselves. They can create users of any type.

    '''

    USER_TYPE = (
        ('ADMIN', 'Administrator'),
        ('TEAML', 'Team Leader'),
        ('RUSER', 'Regular User'),
        ('SUPER', 'Super User'),
    )

    USER_LEVELS = {
        'SUPER': 4,
        'ADMIN': 3,
        'TEAML': 2,
        'RUSER': 1,
        }

    MARKET_CHOICES = (
        ('AD', 'Administration'),
        ('BF', 'BPO Factory'),
        ('BG', 'Behr Germany'),
        ('BK', 'Behr Kirchberg'),
        ('CZ', 'Behr Czech'),
        ('EN', 'MCBC'),
        ('NE', 'Newton'),
        ('SA', 'Store Accounting'),
    )

    PROCESS_CHOICES = (
        ('AD', 'Administration'),
        ('AO', 'Accounting Operations'),
        ('AP', 'Accounts Payable'),
        ('AR', 'Accounts Receivable'),
        ('CP', 'C&A PL'),
        ('CT', 'C&A AT'),
        ('FA', 'F&A'),
        ('HL', 'HRO Lodz'),
        ('HR', 'HRO'),
        ('HW', 'HRO Wro'),
        ('SC', 'Scanning'),
        ('SK', 'C&A CZSK'),
        ('TE', 'Travel & Expenses'),
    )

    JOB_CODES = (
        ('00F20A', '00F20A'),
        ('00F20B', '00F20B'),
        ('00F20C', '00F20C'),
        ('00F20D', '00F20D'),
        ('00F20E', '00F20E'),
        ('00F20F', '00F20F'),
        ('00F20G', '00F20G'),
        ('00000A', 'A'),
        ('00000B', 'B'),
    )

    user_id = models.EmailField(max_length=105,
                                verbose_name=("UserID / HP Email"),
                                unique=True)

    firstname = models.CharField(max_length=60,
                                 db_column='uFirstName',
                                 verbose_name=("First Name"))

    lastname = models.CharField(max_length=60,
                                db_column='uLastName',
                                verbose_name=("Last Name"))

    password = models.CharField(max_length=60,
                                db_column='uPassword')

    user_type = models.CharField(max_length=5,
                                 choices=USER_TYPE)

    market = models.CharField(max_length=2,
                               db_column='uMarket',
                               choices=MARKET_CHOICES)

    process = models.CharField(max_length=2,
                                db_column='uProcess',
                                choices=PROCESS_CHOICES)

    start_date = models.DateField(db_column='Start_Date',
                                  verbose_name=("Start Date"))

    breaklength = models.TimeField(db_column='breakLength',
                                   verbose_name=("Break Length"))

    shiftlength = models.TimeField(db_column='shiftLength',
                                   verbose_name=("Shift Length"))

    job_code = models.CharField(max_length=6,
                                choices=JOB_CODES,
                                db_column='Job_Code',
                                verbose_name=('Job Code'))

    holiday_balance = models.IntegerField(db_column='Holiday_Balance',
                                          verbose_name=('Holiday Balance'))

    disabled = models.BooleanField(db_column='disabled',
                                   verbose_name=('Disabled'))

    class Meta:

        '''
        Metaclass allows for additional options to be set on the model
        '''

        db_table = u'tbluser'
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['user_id']

    def __unicode__(self):

        '''
        How the row is represented in admin

        :note: This method shouldn't be called directly.
        :rtype: :class:`string`
        '''

        return u'%s - %s %s ' % (self.user_id,
                                self.firstname,
                                self.lastname)

    def isdisabled(self):
        '''Returns whether this user is disabled or not'''
        return self.disabled

    def get_shiftlength_list(self):
        '''
        Returns the users' timestring formatted neatly

        :returns: :class:`tuple` of :class:`str` such as ("08:00:00", "17:00:00", "00:15:00")
                  depending on the user's shiftlength
        '''

        start_time = dt.datetime(
            year=1980,
            month=1,
            day=1,
            hour=9,
            minute=0,
            second=0,
            )

        end_time = start_time + dt.timedelta(
            hours=self.shiftlength.hour,
            minutes=self.shiftlength.minute,
            seconds=self.shiftlength.second
            )

        return map(datetime_to_timestring,
                   [start_time, end_time, self.breaklength])

    def get_subordinates(self, get_all=False):
        '''get_subordinates will smartly find which Users are related to
        this User instance.

        In the case of a RUSER then the returned QuerySet will contain
        only those who are under the same manager and have the same
        process type.

        TEAML will return a QuerySet containing their manager and
        their manager's team.

        SUPER and ADMIN will return their linked teams.

        '''
        try:
            if self.is_user():
                return self.get_teammates()
            if self.sup_tl_or_admin():
                if self.is_tl():
                    admin = self.get_administrator()
                else:
                    admin = self
                # find the subordinates and the related users
                if get_all:
                    result = Tblauthorization.objects.get(
                        admin=admin
                        ).users.all()
                else:
                    result = Tblauthorization.objects.get(
                        admin=admin
                        ).users.filter(disabled=False)
                try:
                    extra = RelatedUsers.objects.get(
                        admin=admin
                        ).users.filter(disabled=False)
                except RelatedUsers.DoesNotExist:
                    extra = []

                ids = [user.id for user in result] + [user.id for user in extra]
                # find whether we need to append this user to it.
                if self != admin or self.super_or_admin():
                    ids.append(admin.id)
                return Tbluser.objects.filter(id__in=ids).order_by("lastname")
        except Tblauthorization.DoesNotExist:
            return []

    def get_administrator(self):

        '''Returns the :class:`Tbluser` who is this instances Authorization
        link

        :returns: A :class:`Tbluser` instance
        :rtype: :class:`Tbluser`

        '''

        if self.super_or_admin():
            return self

        try:
            auth_links = Tblauthorization.objects.all().filter(users=self)
            if len(auth_links) == 1:
                return auth_links[0].admin
            if len(auth_links) == 2:
                for link in auth_links:
                    if link.admin.user_type == "SUPER":
                        continue
                    else:
                        return link.admin
            # if we're here we're in a bad state.
            # we use objects.get() due to it throwing
            # the correct Exception.
            Tblauthorization.objects.get(users=self)
        except Tblauthorization.DoesNotExist:
            return self

    def get_teammates(self):
        '''
        Get teammates will return a QuerySet of users which are the same
        process type
        '''
        return Tblauthorization.objects.get(
            admin=self.get_administrator()
            ).users.filter(
            disabled=False, process=self.process
            ).order_by('lastname')

    def display_user_type(self):
        '''
        Function for displaying the user_type in admin.

            :note: This method shouldn't be called directly.
            :rtype: :class:`string`
        '''
        return self.user_type

    def name(self):
        '''Utility method for returning users full name. This is useful for
        when we are pretty printing users and their names. For example
        in e-mails and or when we are displaying users on the
        front-end.

        :rtype: :class:`string`

        '''
        return self.firstname + ' ' + self.lastname

    def rev_name(self):
        '''Returns a user's name formatted in the reversed formal way.

        I.e. "Aaron France" would be "France, Aaron"'''
        return '%s, %s' % (self.lastname, self.firstname)

    def tracking_entries(self,
                         year=None,
                         month=None):
        '''Returns all the tracking entries associated with
        this user.

        This is particularly useful when required to make a report or
        generate a specific view of the tracking entries of the user.

        :param year: The year in which the QuerySet should be filtered
                     by. Defaults to the current year.
        :param month: The month in which the QuerySet should be filtered
                     by. Defaults to the current month.
        :rtype: :class:`QuerySet`

        '''

        if year is None:
            year = dt.datetime.today().year
        if month is None:
            month = dt.datetime.today().month

        return TrackingEntry.objects.filter(user_id=self.id,
                                            entry_date__year=year,
                                            entry_date__month=month)

    def get_comments(self, year):
        '''
        Get Comments will return a formatted string of this users comments
        for a given year.
        '''
        entries =  TrackingEntry.objects.filter(
            user_id=self.id,
            entry_date__year=year
            )
        comments_list = []
        for entry in entries:
            if entry.comments:
                comment_string = map(unicode, [entry.entry_date,
                                               entry.user.name(),
                                               entry.comments])
                comments_list.append(' '.join(comment_string))
        return comments_list

    def year_as_whole(self, year):
        '''Creates an entire year table with the weekends properly labelled as
        well as giving an area to fill in additional html tags and css
        classes.  This is useful for generating a year view on the
        data in some way.
        '''

        final = []
        out = []
        for x in range(1, 13):
            out.append("<tr id=\"%d_row\" onclick=%s><th>%s</th>"
                       % (x, '"highlight_row(%d)"' % x, MONTH_MAP[x-1][1]))
            for z in range(1, 32):
                try:
                    if dt.date(int(year), x, z).isoweekday() in [6, 7]:
                        out.append('<td class="WKEND">%d</td>' % z)
                    else:
                        out.append('<td {function} class={c}>%d</td>' % z)
                except ValueError:
                    out.append('<td {function} class={c}>%d</td>' % z)

            out.append("</tr>")
            final.append(out)
            out = []
        return final

    def yearview(self, year):
        '''Generates the HTML table for the yearview page. It iterates
        through the entire set of tracking entries for a given year.

        :param year: The year in which the yearview should be generated from.
        :type year: :class:`int`
        :rtype :class:`str`

        '''
        entries = TrackingEntry.objects.filter(user_id=self.id,
                                               entry_date__year=year)
        basehtml = self.year_as_whole(year)
        for entry in entries:
            basehtml[entry.entry_date.month-1][entry.entry_date.day] = \
                basehtml[entry.entry_date.month-1][entry.entry_date.day].format(
                c=entry.daytype, function="")
        table_string = ''.join([''.join(subrow) for subrow in basehtml])
        tmpl = get_template("fragments/yearview.html")
        ctx = Context({
            "yearbox": generate_year_box(int(year), id="cmb_yearbox"),
            "comments": self.get_comments(year),
            "balances": ((k, v) for k, v in sorted(self.get_balances(year).items())),
            })
        table_string += tmpl.render(ctx)
        return '<table id="holiday-table"><th colspan=999>%s</th>' \
            % self.name() + table_string

    def overtime_view(self, year):
        '''Generates the HTML table for the overtime_view page. It iterates
        through the entire set of tracking entries for a given year.

        :param year: The year in which the overtime should be generated from.
        :type year: :class:`int`
        :rtype :class:`str`

        '''
        entries = TrackingEntry.objects.filter(user_id=self.id,
                                               entry_date__year=year)
        basehtml = self.year_as_whole(year)
        for entry in entries:
            basehtml[entry.entry_date.month-1][entry.entry_date.day] = \
                basehtml[entry.entry_date.month-1][entry.entry_date.day].format(
                c=entry.overtime_class(),
                function="entry_date='%s'" % entry.entry_date)
        table_string = ''.join([''.join(subrow) for subrow in basehtml])
        # TODO: Template this.
        table_string += '''
<tr>
  <td colspan=100>
    <table>
      <tr>
        <th style="width:10%%">Year</th><td style="width:90%%">{yearbox}</td>
      </tr>
      <tr><th>Agent</th><td>{employees_select}</td></tr>
    </table>
  </td>
</tr>
'''
        return '<table id="holiday-table"><th colspan=999>%s</th>' \
            % self.name() + table_string

    def sup_tl_or_admin(self):
        '''
        This group of functions are helper methods for querying whether
        the user is contained with a certain set of user_types.

        SUPER/TL/ADMIN'''
        return self.user_type in ["SUPER", "ADMIN", "TEAML"]

    def super_or_admin(self):
        '''SUPER/ADMIN'''
        return self.user_type in ["SUPER", "ADMIN"]

    def admin_or_tl(self):
        '''ADMIN/TEAML'''
        return self.user_type in ["ADMIN", "TEAML"]

    def is_super(self):
        '''SUPER'''
        return self.user_type == "SUPER"

    def is_admin(self):
        '''ADMIN'''
        return self.user_type == "ADMIN"

    def is_tl(self):
        '''TEAML'''
        return self.user_type == "TEAML"

    def is_user(self):
        '''RUSER'''
        return self.user_type == "RUSER"

    def get_holiday_balance(self, year):
        '''Calculates the holiday balance for the employee

        This method loops over all :class:`TrackingEntry` entries
        attached to the user instance which are in the year passed in,
        taking each entries day_type and looking that up in a value
        map.

        Values can be:

        1) Holiday: Remove a day
        2) Work on Public Holiday: Add two days
        3) Return for working Public Holiday: Remove a day
        4) Day on Demand: Remove a day
        5) Work on Saturday: Add a day


        :param year: The year in which the holiday balance should be
                     calculated from
        :type year: :class:`int`
        :rtype: :class:`Integer`

        '''

        tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                     entry_date__year=year)

        holiday_value_map = {
            'HOLIS': -1,
            'PUWRK': 2,
            'RETRN': -1,
            'DAYOD': -1,
            'SATUR': 1
            }

        holiday_balance = self.holiday_balance
        for entry in tracking_days:
            holiday_balance += holiday_value_map.get(entry.daytype, 0)

        return holiday_balance

    def get_num_daytype_in_year(self, year, daytype):
        '''
        Base method for retrieving the number of instances of a specific
        daytype in a given year.
        '''
        return len(TrackingEntry.objects.filter(user_id=self.id,
                                            entry_date__year=year,
                                            daytype=daytype))

    def get_dod_balance(self, year):
        '''
        Pass through method for retrieving the DAYOD number in a year
        '''
        return self.get_num_daytype_in_year(year, "DAYOD")

    def get_balances(self, year):
        '''
        Get balances will return a dictionary of long daytype names
        against their balances.
        '''
        daytype_dict = {
            daytype[1]: self.get_num_daytype_in_year(year, daytype[0]) \
                for daytype in DAYTYPE_CHOICES
            }
        daytype_dict.update({
            "Calculated Holidays": self.get_holiday_balance(year)
            })
        return daytype_dict

    def get_thismonths_balance(self, ret="html"):
        '''get_thismonths_balance returns the users balance for this month and
        this month only.

        :param ret: String indicating what return type is required.
        '''
        return self.get_total_balance(ret=ret,
                                      year=dt.datetime.today().year,
                                      month=dt.datetime.today().month)

    def get_last7days(self):
        '''get_last7days returns the users balance for the last seven days.

        :param ret: String indicating what return type is required.
        '''
        today = dt.datetime.today()
        return self.get_total_balance(
            from_=today.replace(**{'day': 1} \
                                if today.day-7 <= 0 \
                                else {'day': today.day-7}),
            to_=today)

    def zeroing_hours(self):
        '''zeroing_hours returns true if the user should have their hours
        zeroed.'''
        return settings.ZEROING_HOURS.get(self.market)

    def get_normalized_balance(self, ret="int"):

        '''get_normalized_balance will automatically figure out whether the
        user in question should have their balance zeroed or not.
        '''

        return self.get_thismonths_balance(ret=ret) if self.zeroing_hours() \
            else self.get_total_balance(ret=ret)

    def get_total_balance(self, ret='html', year=None, month=None,
                          from_=None, to_=None):
        '''Calculates the total balance for the user.

        This method iterates through every :class:`TrackingEntry`
        attached to this user instance which is a working day,
        multiplies the user's shiftlength by the number of days and
        finds the difference between the projected working hours and
        the actual working hours.

        The return type of this function is different depending on the
        argument supplied.

        :note: To customize how the CSS class is determined when using the
               html mode you will need to change the ranges in the
               tracking_class_map attribute.
        :param ret: Determines the return type of the function. If it is not
                    supplied then it defaults to 'html'. If it is 'int' then
                    the function will return an integer, finally, if the
                    string 'dbg' is passed then we output all the values used
                    to calculate and the final value.
        :rtype: :class:`string` or :class:`integer`

        '''

        ret = ret.lower()
        # if the argument isn't supported'
        if ret not in ['html', 'int', 'num', 'flo']:
            raise Exception("Unsupported Argument. Must be html, int or dbg")

        day_types = [element[0]
                     for element in WORKING_CHOICES
                     if element[0] not in ["SATUR","LINKD"]]

        if not year and not month:
            tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                         daytype__in=day_types)
            return_days = TrackingEntry.objects.filter(user_id=self.id,
                                                       daytype="ROVER")
        elif year and not month:
            tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                         daytype__in=day_types,
                                                         entry_date__year=year)
            return_days = TrackingEntry.objects.filter(user_id=self.id,
                                                       daytype="ROVER",
                                                       entry_date__year=year
                                                       )
        else:
            tracking_days = TrackingEntry.objects.filter(
                user_id=self.id,
                daytype__in=day_types,
                entry_date__year=year,
                entry_date__month=month
                )
            return_days = TrackingEntry.objects.filter(user_id=self.id,
                                                       daytype="ROVER",
                                                       entry_date__year=year,
                                                       entry_date__month=month)
        if from_ and to_:
            tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                         daytype__in=day_types,
                                                         entry_date__range=[from_,to_])
            return_days = TrackingEntry.objects.filter(user_id=self.id,
                                                       daytype="ROVER",
                                                       entry_date__range=[from_,to_]
                                                       )

        if settings.OVERRIDE_CALCULATION.get(self.market):
            trackingnumber = \
                settings.OVERRIDE_CALCULATION[self.market](self,
                                                           tracking_days,
                                                           return_days)
        else:
            trackingnumber = \
                self._regular_calculation(tracking_days, return_days)

        if ret == 'html':
            tracker_class_map = {
                # create a map of values which map to the classes
                frozenset(range(-3, 3)): 'class=tracker-val-ok',
                frozenset(range(-6, -3)): 'class=tracker-val-warning',
                frozenset(range(4, 6)): 'class=tracker-val-warning',
            }

            tracking_class = 'class=tracker-val-danger'
            for key in tracker_class_map:
                # look in the map for the balance value to
                # retrieve the class
                if int(trackingnumber) in key:
                    tracking_class = tracker_class_map[key]
                    break

            return "<p %s>%s</p>" % (
                tracking_class,
                float_to_time(trackingnumber)
            )
        elif ret == 'flo':
            return trackingnumber
        elif ret == 'num':
            return int(trackingnumber)
        elif ret == 'int':
            return float_to_time(trackingnumber)

    def _regular_calculation(self, tracking_days, return_days):
        '''This is the calculation that's used as a fall-back in case there
        isn't one being used in-place of this.

        It does not do any rounding and thus will be the exact figures that
        agent's enter.

        '''

        # we'll use augmented assignment
        # so zero our local vars here
        (total_hours, total_mins,
         shift_hours, shift_minutes) = (0, 0, 0, 0)

        for item in tracking_days:
            if item.is_linked():
                continue
            shift_hours += self.shiftlength.hour
            shift_minutes += self.shiftlength.minute

            total_hours += (
                item.end_time.hour
                - item.start_time.hour
                - item.breaks.hour
                )

            total_mins += (
                item.end_time.minute
                - item.start_time.minute
                - item.breaks.minute
                )

        for item in return_days:
            shift_hours += self.shiftlength.hour + self.breaklength.hour
            shift_minutes += self.shiftlength.minute + self.breaklength.minute

        return 0 - (add(shift_hours, (shift_minutes / 60.0))
                           - add(total_hours, (total_mins / 60.0)))

    def balance_breakdown(self):
        '''balance_breakdown returns a tuple of tuples showing a
        pretty-printed version of the users balances for 7 days and
        the last month.

        :return: :class:`tuple` Two tuples containing each a two-tuple
        with a tag for the name and the value for that field.
        '''
        return (
            ("Last 7 Days", self.get_last7days()),
            ("Last Month", self.get_normalized_balance(ret="html"))
        )

    def shiftlength_as_float(self):
        '''Returns the shiftlength of the user as a float
        :rtype: :class:`float`'''
        shift_hours = self.shiftlength.hour + self.breaklength.hour
        shift_minutes = (self.shiftlength.minute
                         + self.breaklength.minute) / 60.0
        return shift_hours + shift_minutes

    def send_pending_overtime_notification(self, send=False):
        '''Determines whether an overtime notification is required and sends
        it.

        :param send: send directly or return the EmailMessage.'''
        if self.get_total_balance(ret='num') > 0:
            return send_pending_overtime_notification(self, send)

    def send_weekly_reminder(self):
        '''
        Sends the weekly reminder for an agent about their holiday balances
        '''
        templ = get_template("emails/weekly_reminder.dhtml")

        prev = self.previous_week_balance()
        expect = self.expected_weekly_balance()
        ctx = Context({
            "previous_week_balance": prev,
            "expected_balance": expect,
            "difference": prev - expect
        })
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = templ.render(ctx)
        email.to = [self.user_id]
        email.subject = "Weekly timetracking reminder"
        email.send()

    def previous_week_balance(self):
        '''Gets the user's previous weekly balance'''
        entries =  TrackingEntry.objects.filter(entry_date__range=(
                dt.datetime.now()+dt.timedelta(days=-7), dt.datetime.now()
                ), user_id=self.id, daytype__in=["SATUR", "WKDAY"])
        total = self.shiftlength_as_float() * (NUM_WORKING_DAYS - len(entries))
        for entry in entries:
            total += entry.totalhours()
        return total

    def expected_weekly_balance(self):
        '''Returns the users normal working balance.'''
        return self.shiftlength_as_float() * NUM_WORKING_DAYS

    def get_manager_email(self):
        '''Returns a list of manager's e-mails for this particular user.'''
        overridden = settings.MANAGER_EMAILS_OVERRIDE.get(self.market)
        if overridden:
            return overridden
        # list because the SMTP module takes lists of emails when
        # sending e-mails.
        return [self.get_administrator().user_id]

    def get_manager_name(self):
        '''Gets the name(s) of the managers for this particular user.'''
        overridden = settings.MANAGER_NAMES_OVERRIDE.get(self.market)
        if overridden:
            return ',\n'.join(overridden)
        return self.get_administrator().name()

    def shouldnotifysick(self, entry):
        '''shouldnotifysick determintes whether the entry and the 30 days
        previous to it require us to send out a notification to the
        manager extolling that the user has gone over the allowed
        amount of sickdays and thus may require to be taken off the
        Action Reports.

        :param entry: The entry to do the search from.
        :return: Boolean.
        '''
        thirtydaysago = entry.entry_date + dt.timedelta(days=-30)
        previous30days = TrackingEntry.objects.filter(
            user_id=self.id,
            daytype="SICKD",
            entry_date__range=[thirtydaysago, entry.entry_date]
        )
        return len(previous30days) >= 30

    def sendsicknotification(self):
        '''sendsicknotification actually performs the sick notification to the
        manager.
        '''
        tmpl = get_template("emails/sick_notification.dhtml")
        ctx = Context({
            "employee": self.name()
        })
        message_manager = EmailMessage(
            from_email='timetracker@unmonitored.com'
        )
        message_manager.body = tmpl.render(ctx)
        message_manager.to = self.get_manager_email()
        message_manager.subject = "Sick leave >= 30 days: %s" % \
                                  self.name()
        message_manager.send()

    def approval_notifications(self):
        '''approval_notifications will generate the required HTML for
        displaying approval notifications in the navigation bar. We
        return an empty string if there are no approval notifications
        pending or a span with the relevant information inside it if
        there are any.

        :return: :class:`str`
        '''
        if self.is_user():
            return ""
        return "<span class=\"notifications\">%d</span>" % len(
            self.get_approvals()
        )

    def get_approvals(self):
        '''Returns the approvals associated with this team's user.'''
        # to avoid circular import dependencies
        from timetracker.overtime.models  import PendingApproval
        return PendingApproval.objects.filter(
            closed=False, approver=self.get_administrator()
        )

    def has_pending_approvals(self):
        '''Returns whether this user has any pending approvals in their
        queue.'''
        return bool(len(self.get_approvals()))

    @staticmethod
    def manager_emails_for_account(account):
        '''Gets the e-mails for the managers for the whole account.'''
        admins = Tbluser.objects.filter(
            user_type__in=["ADMIN", "TEAML"],
            market=account
            )
        return [admin.user_id for admin in admins]

    @staticmethod
    def administrator_emails_for_account(account):
        '''Gets the e-mails for the administrators for the whole account.'''
        admins = Tbluser.objects.filter(
            user_type="ADMIN",
            market=account
            )
        return [admin.user_id for admin in admins]

    @staticmethod
    def all_emails_for_account(account):
        '''Gets all e-mails for the whole account.'''
        users = Tbluser.objects.filter(
            market=account
            )
        return [user.user_id for user in users]

class UserForm(ModelForm):
    '''Form class the for Tbluser'''
    class Meta:
        '''Options.'''
        model = Tbluser

class RelatedUsers(models.Model):
    '''
    Related users offers similar functionality to the Tblauthorization
    table except without the baggage of it being automatically populated
    when users are created.
    '''

    admin = models.ForeignKey(
        Tbluser,
        related_name="related_foreign"
    )

    users = models.ManyToManyField(
        Tbluser,
        related_name="related_view",
        verbose_name=("Additional Users")
    )

    class Meta:

        '''
        Metaclass gives access to additional options
        '''

        db_table = u'tblrelatedusers'
        verbose_name = "Related User"
        verbose_name_plural = "Related Users"

    def __unicode__(self):

        '''
        Admin view uses this to display the entry
        '''
        return unicode(self.admin)

    def display_users(self):

        '''
        Method which generates the HTML for the admin views
        :rtype: :class:`string`
        '''

        table_header = u'''
                       <table>
                         <tr>
                          <th>Name</th>
                         </tr>
                       '''

        table_data_string = u'''
                            <tr>
                              <td>{0}</td>
                            </tr>
                            '''

        table_inner_list = [
            table_data_string.format(user.name())
            for user in self.users.all().order_by('lastname')
        ]

        return u''.join([
            table_header,
            u''.join([table_entry for table_entry in table_inner_list]),
            '</table>']
        )

    display_users.allow_tags = True
    display_users.short_discription = "Related Users"


class Tblauthorization(models.Model):

    '''Links Administrators (managers) with their team.

    This table is a many-to-many relationship between Administrators
    and any other any user type in TEAML/RUSER.

    This table is used to explicitly show which people are in an
    Administrator's team. Usually in SQL-land, you would be able to
    instanstiate multiple rows of many-to-many relationships, however,
    due to the fact that working with these tables in an object
    orientated fashion is far simpler adding multiple relationships to
    the same :class:`Tblauthorization` object, we re-use the
    relationship when creating/adding additional
    :class:`Tblauthorization` instances.

    This means that, if you were to need to add a relationship between
    an Administrator and a RUSER, then you would need to make sure
    that you retrieve the :class:`Tblauthorization` object *before*
    and save the new link using that instance. Failure to do this
    would mean that areas where the .get() method is employed would
    start to throw Tblauthorization.MultipleObjectsReturned.

    In future, and time, I would like to make it so that the .save()
    method is overloaded and then we can check if a
    :class:`Tblauthorization` link already exists and if so, save to
    that instead.

    '''

    admin = models.ForeignKey(
        Tbluser,
        limit_choices_to={
            'user_type__in': ['SUPER', 'ADMIN']
        },
        related_name="admin_foreign"
    )

    users = models.ManyToManyField(
        Tbluser,
        limit_choices_to={
            'user_type__in': ['TEAML', 'RUSER', 'ADMIN']
        },
        related_name="subordinates",
        verbose_name=("Additional Users")
    )

    class Meta:

        '''
        Metaclass gives access to additional options
        '''

        db_table = u'tblauthorization'
        verbose_name = "Authorization Link"
        verbose_name_plural = "Authorization Links"

    def __unicode__(self):

        '''
        Admin view uses this to display the entry
        '''
        return unicode(self.admin)

    def display_users(self):

        '''
        Method which generates the HTML for the admin views
        :rtype: :class:`string`
        '''

        table_header = u'''
                       <table>
                         <tr>
                          <th>Name</th>
                         </tr>
                       '''

        table_data_string = u'''
                            <tr>
                              <td>{0}</td>
                            </tr>
                            '''

        table_inner_list = [
            table_data_string.format(user.name())
            for user in self.users.all().order_by('lastname')
        ]

        return u''.join([
            table_header,
            u''.join([table_entry for table_entry in table_inner_list]),
            '</table>']
        )

    display_users.allow_tags = True
    display_users.short_discription = "Subordinate Users"


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

    user = models.ForeignKey(Tbluser, related_name="user_tracking")
    link = models.OneToOneField("self", related_name="linked_entry",
                                null=True, blank=True)
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

    @staticmethod
    def headings():
        '''Describes this class as if it were a CSV heading bar.'''
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
        try:
            user.get_subordinates().get(id=self.user.id)
            return True
        except Tbluser.DoesNotExist:
            suspicious_log.critical(
                "An accept/edit check was made by %s for an entry which " \
                % self.name() + \
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
            if self.link.daytype == "LINKD":
                self.link.delete()
            else:
                self.link.link = None
                self.link.save()

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
        templ = get_template("emails/holiday_approved.dhtml")
        ctx = Context({
            "entry_date": str(self.entry_date)
            })
        email = EmailMessage(from_email='timetracker@unmonitored.com')
        email.body = templ.render(ctx)
        email.to = [self.user.user_id]
        email.subject = "Holiday Request: Approved."
        email.send()
