from django.contrib import admin
from django.core.mail import send_mail

from timetracker.tracker import models
from timetracker.utils.error_codes import CONNECTION_REFUSED

def send_password_reminder(modeladmin, request, queryset):

    '''
    Send an e-mail reminder to all the selected employees
    '''
    email_message = "Hi {name},\n\tYour password is {password}\nRegards,"
    for user in queryset:

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


class UserAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'display_user_type')
    actions = [send_password_reminder]

class AuthAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'display_users')


class TrackerAdmin(admin.ModelAdmin):
    def clean_entry_date(self):
        print 'lolwat'


admin.site.register(models.Tbluser, UserAdmin)
admin.site.register(models.TrackingEntry, TrackerAdmin)
admin.site.register(models.Tblauthorization, AuthAdmin)
