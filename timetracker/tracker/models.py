'''
Definition of the models used in the timetracker app
'''

import datetime as dt

from operator import add

from django.db import models
from django.forms import ModelForm

from timetracker.utils.datemaps import (
    WORKING_CHOICES, DAYTYPE_CHOICES, float_to_time
    )


class Tbluser(models.Model):

    """
    Models the user table and provides the admin interface with the
    niceties it needs.
    """

    USER_TYPE = (
        ('ADMIN', 'Administrator'),
        ('TEAML', 'Team Leader'),
        ('RUSER', 'Regular User')
    )

    MARKET_CHOICES = (
        ('BG', 'Germany'),
        ('BK', 'Kirchberg'),
        ('CZ', 'Czech')
    )

    PROCESS_CHOICES = (
        ('AP', 'Accounts Payable'),
        ('AR', 'Accounts Receivable'),
        ('AO', 'Accounting Operations')
    )

    JOB_CODES = (
        ('00F20A', '00F20A'),
        ('00F20B', '00F20B'),
        ('00F20C', '00F20C'),
        ('00F20D', '00F20D'),
        ('00F20E', '00F20E'),
        ('00F20F', '00F20F'),
        ('00F20G', '00F20G')
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

    class Meta:

        """
        Metaclass allows for additional options to be set on the model
        """

        db_table = u'tbluser'
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __unicode__(self):

        """
        How the row is represented in admin
        """

        return '%s - %s %s ' % (self.user_id,
                                self.firstname,
                                self.lastname)

    def get_administrator(self):

        """
        Returns the administrator associated with this
        """
        try:
            return Tblauthorization.objects.get(users=self).admin
        except Tblauthorization.DoesNotExist:
            return self

    def display_user_type(self):

        """
        Function for displaying the user in admin
        """

        return self.user_type

    def name(self):

        """
        Utility method for returning users full name
        """

        return self.firstname + ' ' + self.lastname

    def tracking_entries(self,
                         year=dt.datetime.today().year,
                         month=dt.datetime.today().month):
        """
        Returns all the tracking entries associated with
        this user
        """

        return TrackingEntry.objects.filter(user_id=self.id,
                                            entry_date__year=year,
                                            entry_date__month=month)

    def is_admin(self):
        """
        Returns whether or not the user instance is an admin
        """

        return self.user_type in ["ADMIN", "TEAML"]

    def get_holiday_balance(self, year):
        """
        Calculates the holiday balance for the employee
        """

        tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                     entry_date__year=year)

        holiday_value_map = {
            'HOLIS': -1,
            'PUWRK': 2,
            'RETRN': -1
            }

        holiday_balance = self.holiday_balance
        for entry in tracking_days:
            holiday_balance += holiday_value_map.get(entry.daytype, 0)

        return holiday_balance

    def get_total_balance(self, ret='html'):

        """
        Calculates the total balance for the user.
        """

        # we'll use augmented assignment
        # so zero our local vars here
        (trackingnumber, total_hours, total_mins,
         shift_hours, shift_minutes) = (0, 0, 0, 0, 0)

        day_types = [element[0] for element in WORKING_CHOICES]
        tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                     daytype__in=day_types)

        for item in tracking_days:
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

        trackingnumber = 0 - (add(shift_hours, (shift_minutes / 60.0))
                           - add(total_hours, (total_mins / 60.0)))

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

        elif ret == 'int':
            return float_to_time(trackingnumber)
        elif ret == 'dbg':
            return (trackingnumber, total_hours, total_mins,
                    shift_hours, shift_minutes)


class UserForm(ModelForm):

    class Meta:
        model = Tbluser


class Tblauthorization(models.Model):

    """
    Links Administrators (managers) with their team.
    """

    admin = models.ForeignKey(
        Tbluser,
        limit_choices_to={
        'user_type': 'ADMIN'
        },
        related_name="admin_foreign"
    )

    users = models.ManyToManyField(
        Tbluser,
        limit_choices_to={
        'user_type__in': ['TEAML', 'RUSER']
        },
        related_name="subordinates",
        verbose_name=("Additional Users")
    )

    class Meta:

        """
        Metaclass gives access to additional options
        """

        db_table = u'tblauthorization'
        verbose_name = "Authorization Link"
        verbose_name_plural = "Authorization Links"

    def __unicode__(self):

        """
        Admin view uses this to display the entry
        """

        return str(self.admin)

    def display_users(self):

        """
        Method which generates the HTML for the admin views
        """

        table_header = """
                       <table>
                         <tr>
                          <th>Name</th>
                         </tr>
                       """

        table_data_string = """
                            <tr>
                              <td>{0}</td>
                            </tr>
                            """

        table_inner_list = [
            table_data_string.format(user.name())
            for user in self.users.all()
        ]

        return ''.join([
            table_header,
            ''.join([table_entry for table_entry in table_inner_list]),
            '</table>']
        )

    display_users.allow_tags = True
    display_users.short_discription = "Subordinate Users"


class TrackingEntry(models.Model):

    """
    Entry for a specific day
    """

    user = models.ForeignKey(Tbluser, related_name="user_tracking")

    entry_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    breaks = models.TimeField()
    daytype = models.CharField(choices=DAYTYPE_CHOICES,
                               max_length=5)

    comments = models.TextField(blank=True)

    class Meta:

        """
        Metaclass gives access to additional options
        """

        verbose_name = 'Daily Tracking Log'
        verbose_name_plural = 'Daily Tracking Logs'
        unique_together = ('user', 'entry_date')

    def __unicode__(self):

        """
        Method to display entry in admin
        """

        date = '/'.join(
            map(str,
                [self.entry_date.year,
                 self.entry_date.month,
                 self.entry_date.day
                 ])
            )

        return str(self.user) + ' - ' + date
