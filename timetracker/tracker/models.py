'''
Definition of the models used in the timetracker app
'''

from django.db import models
from django.forms import ModelForm

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

    def __unicode__(self):

        """
        How the row is represented in admin
        """

        return '%s - %s %s ' % (self.user_id,
                                self.firstname,
                                self.lastname)
    
    def get_total_balance(self):

        """
        Calculates the total balance for the user.
        """

        total, total_mins = 0, 0
        tracking_days = TrackingEntry.objects.filter(user_id=self.id)
        
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

        return "<p %s> %s </p>" % (tracking_class, trackingnumber)

    class Meta:

        """
        Metaclass allows for additional options to be set on the model
        """

        db_table = u'tbluser'
        verbose_name = "User"
        verbose_name_plural = "Users"
        unique_together = ("user_id", "firstname", "lastname")

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
        to_out("""<option value=null>---</option>""")
        to_out("""</select>""")

        return ''.join(str_output)

    display_users.allow_tags = True
    display_users.short_discription = "Subordinate Users"

    def __unicode__(self):

        """
        Adming view uses this to display the entry
        """

        return str(self.admin)

    class Meta:

        """
        Metaclass gives access to additional options
        """

        db_table = u'tblauthorization'
        verbose_name = "Authorization Link"
        verbose_name_plural = "Authorization Links"


class TrackingEntry(models.Model):

    """
    Entry for a specific day
    """

    DAYTYPE_CHOICES = (
        ('WKDAY', 'Work Day'),
        ('SICKD', 'Sickness Absence'),
        ('HOLIS', 'Scheduled Holiday'),
        ('SPECI', 'Special Circumstances'),
        ('OTHER', 'Other'),
    )

    user = models.ForeignKey(Tbluser, related_name="user_tracking")

    entry_date = models.DateField()
    start_time = models.TimeField(blank=False)
    end_time = models.TimeField(blank=False)
    breaks = models.TimeField(blank=False)
    daytype = models.CharField(choices=DAYTYPE_CHOICES,
                               max_length=5)

    comments = models.TextField(blank=True)


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

    class Meta:

        """
        Metaclass gives access to additional options
        """

        verbose_name = 'Daily Tracking Log'
        verbose_name_plural = 'Daily Tracking Logs'
        unique_together = ('user', 'entry_date')
