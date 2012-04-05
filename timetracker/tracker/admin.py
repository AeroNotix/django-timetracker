from timetracker.tracker import models
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'display_user_type')

class AuthAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'display_users')

class TrackerAdmin(admin.ModelAdmin):
    def clean_entry_date(self):
        print 'lolwat'
    
admin.site.register(models.Tbluser, UserAdmin)
admin.site.register(models.TrackingEntry, TrackerAdmin)
admin.site.register(models.Tblauthorization, AuthAdmin)
