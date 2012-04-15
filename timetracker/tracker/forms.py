from django import forms

DAYTYPE_CHOICES = (
    ('WKDAY', 'Work Day'),
    ('SICKD', 'Sickness Absence'),
    ('HOLIS', 'Scheduled Holiday'),
    ('SPECI', 'Special Circumstances'),
    ('OTHER', 'Other'),
)

class EntryForm(forms.Form):
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
    
    
class AddForm(forms.Form):
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


class Login(forms.Form):

    """
    Basic login form
    """
    
    user_name = forms.CharField(
        label="Username:"
    )
    
    user_name.widget.attrs.update({'class': 'login-form',
                                   'id': 'login-user'})
    
    password = forms.CharField(
        label="Password:",
        widget=forms.PasswordInput()
    )
    
    password.widget.attrs.update({'class': 'login-form',
                                  'id': 'login-password'})

