from django import forms

DAYTYPE_CHOICES = (
    ('WKDAY', 'Work Day'),
    ('SICKD', 'Sickness Absence'),
    ('HOLIS', 'Scheduled Holiday'),
    ('SPECI', 'Special Circumstances'),
    ('OTHER', 'Other'),
)

class entry_form(forms.Form):
    """
    Change entry form
    """

    entry_date = forms.DateField(label="Entry Date:")
    entry_date.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_entrydate',
                                    'readonly': 'readonly'})

    start_time = forms.TimeField(label="Start Time:")
    start_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_starttime'})

    end_time = forms.TimeField(label="End Time:")
    end_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_endtime'})

    daytype = forms.ChoiceField(label="Day Type:", choices=DAYTYPE_CHOICES)
    daytype.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_daytype'})
    
    
class add_form(forms.Form):
    """
    Add entry form
    """

    entry_date = forms.DateField(label="Entry Date:")
    entry_date.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_entrydate',
                                    'readonly': 'readonly'})

    start_time = forms.TimeField(label="Start Time:")
    start_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_starttime'})

    end_time = forms.TimeField(label="End Time:")
    end_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_endtime'})

    daytype = forms.ChoiceField(label="Day Type:", choices=DAYTYPE_CHOICES)
    daytype.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_daytype'})
