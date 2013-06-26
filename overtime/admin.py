from django.contrib import admin

from timetracker.overtime import models


class PendingApprovalAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.PendingApproval, PendingApprovalAdmin)
