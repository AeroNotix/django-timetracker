'''
Forms used for user input for the tracker app
'''

from django import forms
from timetracker.utils.datemaps import DAYTYPE_CHOICES


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
                                    'id': 'change_starttime',
                                    'maxlength': '5'})

    end_time = forms.TimeField(label="End Time:")
    end_time.widget.attrs.update({'class': 'change-el',
                                  'id': 'change_endtime',
                                'maxlength': '5'})

    breaks = forms.TimeField(label="Breaks:")
    breaks.widget.attrs.update({'class': 'change-el',
                                'id': 'change_breaks',
                                'maxlength': '5'})

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
                                    'id': 'add_starttime',
                                    'maxlength': '5'})

    end_time = forms.TimeField(label="End Time:")
    end_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_endtime',
                                  'maxlength': '5'})

    breaks = forms.TimeField(label="Breaks:")
    breaks.widget.attrs.update({'class': 'change-el',
                                'id': 'add_breaks',
                                'maxlength': '5'})

    daytype = forms.ChoiceField(label="Day Type:", choices=DAYTYPE_CHOICES)
    daytype.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_daytype',
                                 'maxlength': '5'})


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
