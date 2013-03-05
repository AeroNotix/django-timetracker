Settings files
==============

This documentation will only highlight what is not vanilla Django. If you do not
understand how Django works or the settings it requires, use the Django documentation.

NUM_WORKING_DAYS
----------------

Set this to the number of working days in a normal working week, will default
to five.

DAY_ON_DEMAND_ALLOWANCE
-----------------------

Set this to the number of days on demand an agent is allowed to take in one
year.

MANAGER_EMAILS_OVERRIDE
-----------------------

This is a map between the Tbluser.market short string and a list of e-mails
which will override what is normally used when finding the manager e-mails for
a given account. A use case is where different managers are points of contact
for a given process/account.

.. code-block:: python

    MANAGER_EMAILS_OVERRIDE = {
        "BF": ["example@test.com", "someone@else.com"],
        "CZ": ["aaron.france@hp.com"]
    }

MANAGER_NAMES_OVERRIDE
-----------------------

This is a map between the Tbluser.market short string and a list of names
which will override what is normally used when finding the manager names for
a given account. A use case is where different managers are points of contact
for a given process/account.

.. code-block:: python

    MANAGER_NAMES_OVERRIDE = {
        "BF": ["Joe Bloggs", "Jan Kowalski"],
        "CZ": ["Aaron France"]
    }

EMAIL_DEBUG
-----------

When testing any functionality related to e-mails, set this to the appropriate
value as well as: `EMAIL_BACKEND` to
'django.core.mail.backends.console.EmailBackend' in order to dump e-mails to
your terminal rather than actually sending e-mails.

FONT_DIRECTORY
--------------

Reports are generated using a specific font (Droid-ttf), point this directory
to the directory where your fonts are installed.

DEFAULT_OT_THRESHOLD
--------------------

When determining if tracking entries are deemed over or undertime, we use a
threshold as to not spam users who are only a few minutes either side. If there
is no specific account setting (see: `OT_THRESHOLD`) then this value is used.
The values are in hours.
Defaults to 0.

OT_THRESHOLDS
-------------

If specific accounts need to have their over or under time thresholds set to
different values, then you can do so here:

.. code-block:: python

    OT_THRESHOLDS = {
        "BF": 0.5
    }

UNDER_TIME_ENABLED
------------------

If specific accounts need to have their undertime tracked then we can enable
or disable the accounts using this.

.. code-block:: python

    UNDER_TIME_ENABLED = {
        "BF": True
    }
