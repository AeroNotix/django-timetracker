from django.contrib import admin

from timetracker.overtime import models


class PendingApprovalAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.pop('using', None)
        kwargs['queryset'] = db_field.rel.to._default_manager.using(db).complex_filter(db_field.rel.limit_choices_to).select_related()
        return super(PendingApprovalAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.PendingApproval, PendingApprovalAdmin)
