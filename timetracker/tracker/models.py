'''
Definition of the models used in the timetracker app
'''

import datetime as dt
import calendar as cdr

from django.db import models
from django.forms import ModelForm

from timetracker.utils.datemaps import (MONTH_MAP, DAYTYPE_CHOICES,
                                        generate_select)

class Tbluser(models.Model):

    """
    Models the user table and provides the admin interface with the
    niceties it needs.
    """

    USER_TYPE = (
        ('ADMIN', 'Administrator'),
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
                                verbose_name=("UserID / HP Email"))

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
        unique_together = ("user_id", "firstname", "lastname")

    def __unicode__(self):

        """
        How the row is represented in admin
        """

        return '%s - %s %s ' % (self.user_id,
                                self.firstname,
                                self.lastname)

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

    def get_total_balance(self):

        """
        Calculates the total balance for the user.
        """

        total, total_mins = 0, 0
        tracking_days = TrackingEntry.objects.filter(user_id=self.id,
                                                     daytype="WKDAY")

        for item in tracking_days:

            total += (      item.end_time.hour
                        - item.start_time.hour )

            total_mins += (     item.end_time.minute
                            - item.start_time.minute )

        trackingnumber =    (     len(tracking_days) * self.shiftlength.hour) \
                              -  (total + (total_mins / 60.0)               )

        tracker_class_map = {
            # create a map of values which map to the classes
            frozenset(range(1)) : 'class=tracker-val-ok',
            frozenset(range(-3, 0)) : 'class=tracker-val-warning',
            frozenset(range(1, 4)) : 'class=tracker-val-warning',
            }

        tracking_class = "class=tracking-val-danger"
        for key in tracker_class_map:
            # look in the map for the balance value to
            # retrieve the class
            if int(trackingnumber) in key:
                tracking_class = tracker_class_map[key]

        return "<p %s> %.2f </p>" % (tracking_class, trackingnumber)

class UserForm(ModelForm):

    class Meta:
        model = Tbluser

class Tblauthorization(models.Model):

    """
    Links Administrators (managers) with their team.
    """

    admin = models.ForeignKey(Tbluser,
                              limit_choices_to = {
                               'user_type':'ADMIN'
                              },
                              related_name="admin_foreign"

                   )

    users = models.ManyToManyField(Tbluser,
                                   limit_choices_to = {
                                    'user_type':'RUSER'
                                   },
                                   related_name="subordinates",
                                   verbose_name = ("Additional Users")
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
                              <td>{0} {1}</td>
                            </tr>
                            """

        table_inner_list = [
            table_data_string.format(user.firstname, user.lastname)
            for user in self.users.all()
        ]

        return ''.join([
            table_header,
            ''.join([table_entry for table_entry in table_inner_list]),
            '</table>']
        )

    def as_option_list(self):

        """
        Outputs an option
        """

        str_output = []
        to_out = str_output.append

        to_out("""<select id="user_select">\n""")

        for user in self.users.all():
            to_out("""\t<option value=%s>%s</option>\n""" % (user.id,
                                                             user.name()))
        to_out("""<option value=null>----------</option>""")
        to_out("""</select>""")

        return ''.join(str_output)


    def gen_holiday_list(self,
                         year=dt.datetime.today().year,
                         month=dt.datetime.today().month):

        """
        Outputs a holiday calendar for that month.

        For each user we get their tracking entries,
        then iterate over each of their entries
        checking if it is a holiday or not, if it is
        then we change the class entry for that number
        in the day class' dict.

        Adds a submit button along with passing the
        user_id to it.
        """

        # we convert the arguments to ints because
        # we get given unicode objects
        year, month = int(year), int(month)

        str_output = []
        to_out = str_output.append
        to_out('<table year=%s month=%s id="holiday-table">' % (year, month))
        to_out("""<tr>
                     <th align="centre" colspan="100">{0}</th>
                  </tr>""".format(MONTH_MAP[month-1][1]))

        # generate the calendar, flatten it and
        # get rid of the zeros
        calendar_array = list()
        for week in cdr.monthcalendar(year, month):
            calendar_array.extend(week)
        calendar_array = filter((lambda x: x > 0), calendar_array)

        for user in self.users.all():
            day_classes = {
                num: 'empty' for num in calendar_array
            }

            # We have a dict with each day as currently
            # empty, we iterate through the tracking
            # entries and apply the daytype from that.
            for entry in user.tracking_entries(year, month):
                day_classes[entry.entry_date.day] = entry.daytype

            # output the table row title, which contains:-
            # Full name, Holiday Balance and the User's
            # job code.
            to_out("""
                   <tr>
                     <th class="user-td">%s</th>
                       <td>%s</td>
                       <td>%s</td>""" % (user.name(),
                                         user.get_holiday_balance(year),
                                         user.job_code
                                         )
                   )

            # We've mapped the users' days to the day number,
            # we can write the user_id as an attribute to the
            # table data and also the dayclass for styling,
            # also, the current day number so that the table
            # shows what number we're on.
            for klass, day in day_classes.items():
                to_out('<td usrid=%s class=%s>%s\n' % (user.id, day, klass))

            # user_id is added as attr to make mass calls
            to_out("""<td>
                        <input value="submit" type="button" user_id="{0}"
                               onclick="submit_holidays({0})" />
                      </td>""".format(user.id))
            to_out('</tr>')

        # generate the data for the year select box
        year_select_data = [(y, y) for y in range(year, year-3, -1)]
        year_select_data.extend( [(y, y) for y in range(year+1, year+3)] )
        year_select_data.sort()

        # generate the data for the month select box
        month_select_data = [(month_num + 1, month[1])
                             for month_num, month in MONTH_MAP.items()]

        # generate the select box for the years
        year_select = generate_select(year_select_data, id="year_select")
        # generate the selecte box for the months
        month_select = generate_select(month_select_data, id="month_select")
        # generate submit all button
        to_out("""<tr>
                    <td colspan="100" align="right">
                      <input id="change_table_data" value="Change" type="button" onclick="change_table_data()" />
                      {0} {1}
                      <input id="submit_all" value="Submit All" type="button" onclick="submit_all()" />
                    </td>
                  </tr>""".format(year_select, month_select))

        return ''.join(str_output)

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
