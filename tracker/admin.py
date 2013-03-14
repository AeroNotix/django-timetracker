'''This module directly deals with how models are interacted with in the admin
interface. This has no direct impact for users but it is useful for webmasters
administrating the application.
'''

from django.contrib import admin
from django.core.mail import send_mail

from timetracker.tracker import models
from timetracker.utils.error_codes import CONNECTION_REFUSED


def send_password_reminder(modeladmin, request, queryset):

    '''Send an e-mail reminder to all the selected employees.

    This appears as an option in the 'Action' list in the admin interface for
    when editing the tbluser instances. This allows you to send an e-mail
    reminder en masse to all users selected.
    '''
    for user in queryset:
        user.send_password_reminder()

        info = {
            'name': user.firstname,
            'password': user.password
        }

        try:
            send_mail(
                "Password Reminder",
                email_message.format(**info),
                "timetracker@unmonitored.com",
                [user.user_id]
            )
        except Exception as error:
            if error[0] == CONNECTION_REFUSED:
                print email_message.format(**info),

def create_100_random_users(modeladmin, request, queryset):
    '''Creates 100 random users for testing purposes.'''
    import random
    import datetime

    for x in range(100):
        randstr = ''.join(chr(random.choice(range(65,91))) for x in range(5))
        models.Tbluser.objects.create(
            user_id="%s@test.com" %  randstr,
            firstname=randstr,
            lastname=randstr,
            password=randstr,
            user_type="RUSER",
            market="BG",
            process="AP",
            start_date=datetime.datetime.today(),
            breaklength="00:15:00",
            shiftlength="08:00:00",
            job_code="00F20G",
            holiday_balance=20
            )


class UserAdmin(admin.ModelAdmin):
    """Creates access to and customizes the admin interface to the tbluser
    instances. We give the list_display of __unicode__ and a 2nd type of
    display_user_tyep because this shows the printed representation of these
    values and makes it easier to navigate a large selection of users.

    actions is a list of functions which are in the 'Actions' list, there is a
    default value of 'delete selected <table>' which Django inserts
    automatically. We add here the send_password_reminder function defined
    above.   
    """
    list_display = ('__unicode__', 'display_user_type', 'disabled')
    actions = [send_password_reminder, create_100_random_users]

class RelatedAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)
    """Creates access to and customizes the admin interface to the
    Tblauthorization instances. We add the __unicode__ and the display_users
    functions so that the display allows us to view the team associated with
    the administrator and the administrator's printed representation.
    """
    list_display = ('__unicode__', 'display_users')


class AuthAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)
    """Creates access to and customizes the admin interface to the
    Tblauthorization instances. We add the __unicode__ and the display_users
    functions so that the display allows us to view the team associated with
    the administrator and the administrator's printed representation.
    """
    list_display = ('__unicode__', 'display_users')


class TrackerAdmin(admin.ModelAdmin):
    """Creates access to and customizes the admin interface to the
    TrackingEntry instances. We have no special functions or list_display
    additions because the default values are useful enough as the interface to
    edit these items is far more useful and better programmed than the basic
    model editor the admin interface provides.
    """
    pass


admin.site.register(models.Tbluser, UserAdmin)
admin.site.register(models.TrackingEntry, TrackerAdmin)
admin.site.register(models.Tblauthorization, AuthAdmin)
admin.site.register(models.RelatedUsers, RelatedAdmin)
