'''Forms used for user input for the tracker app

Several forms are extremely simple and thus it's not required to 'hard-code'
them into HTML templates, which would couple our output with the view
functions which simply isn't good MVC practice.

Module Overview

=========================  ========================
..                         ..
=========================  ========================
:class:`EntryForm`         :class:`AddForm`
:class:`Login`
=========================  ========================
'''

from django import forms
from timetracker.utils.datemaps import DAYTYPE_CHOICES


class EntryForm(forms.Form):
    """Change entry form

    This Class creates a form which allows users to change an existing entry
    which they have added to the timetracking portion of the site. The fields
    match up precisely to the :class:`AddForm` because the data will be the
    same. We have duplicated the code here because we need to explicitly set
    the id values using the widget.attrs.update on the widget dict. This is so
    that each widget could be styled individually and so that we have
    something easily accessbile by front-end javascript code.
    """

    entry_date = forms.DateField(label="Entry Date:")
    entry_date.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_entrydate',
                                    'readonly': 'readonly'})

    start_time = forms.TimeField(label="Start Time:")
    start_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_starttime',
                                    'readonly': 'readonly'})

    end_time = forms.TimeField(label="End Time:")
    end_time.widget.attrs.update({'class': 'change-el',
                                  'id': 'change_endtime',
                                  'readonly': 'readonly'})

    breaks = forms.TimeField(label="Breaks:")
    breaks.widget.attrs.update({'class': 'change-el',
                                'id': 'change_breaks',
                                'readonly': 'readonly'})

    daytype = forms.ChoiceField(label="Day Type:", choices=DAYTYPE_CHOICES)
    daytype.widget.attrs.update({'class': 'change-el',
                                    'id': 'change_daytype'})


class AddForm(forms.Form):
    """Add entry form

    This Class creates a form which allows users to add an entry into the
    timetracking portion of the app. See :class:`ChangeEntry` for a detailed
    description of these two classes as they have a high coupling factor.
    """

    entry_date = forms.DateField(label="Entry Date:")
    entry_date.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_entrydate',
                                    'readonly': 'readonly'})

    start_time = forms.TimeField(label="Start Time:")
    start_time.widget.attrs.update({'class': 'change-el',
                                    'id': 'add_starttime',
                                    'readonly': 'readonly'})

    end_time = forms.TimeField(label="End Time:")
    end_time.widget.attrs.update({'class': 'change-el',
                                  'id': 'add_endtime',
                                  'readonly': 'readonly'})

    breaks = forms.TimeField(label="Breaks:")
    breaks.widget.attrs.update({'class': 'change-el',
                                'id': 'add_breaks',
                                'readonly': 'readonly'})

    daytype = forms.ChoiceField(label="Day Type:", choices=DAYTYPE_CHOICES)
    daytype.widget.attrs.update({'class': 'change-el',
                                 'id': 'add_daytype'})


class Login(forms.Form):

    """ Basic login form

    This form renders into a very simple login field, with fields identified
    differently, both for styling and the optional javascript by-name
    handling. Whilst this form is extremely simple, coding one each and
    every time we wish to use one is just dumb and it's much easier to code it
    once and import it into our project.
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
