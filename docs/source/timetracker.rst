Timetracker API and code
========================

Here I will outline the API for the timetracker application and any advice I
have pertaining to the inner-workings of the code itself.

* :ref:`django_req`
* :ref:`utility`
* :ref:`tracker`
* :ref:`reporting`


.. _django_req:

Django Required
===============

timetracker.views and timetracker.urls
--------------------------------------

.. automodule:: timetracker.views
   :members:

.. automodule:: timetracker.urls
   :members:

timetracker.middleware.exception_handler
----------------------------------------

.. automodule:: timetracker.middleware.exception_handler
   :members:

.. _utility:

Utility Modules
===============

timetracker.utils.calendar_utils
--------------------------------

.. automodule:: timetracker.utils.calendar_utils
   :members:

timetracker.utils.datemaps
--------------------------

.. automodule:: timetracker.utils.datemaps
   :members:

timetracker.utils.error_codes
-----------------------------

.. automodule:: timetracker.utils.error_codes
   :members:

timetracker.utils.decorators
----------------------------

.. automodule:: timetracker.utils.decorators
   :members:

timetracker.loggers
-------------------

.. automodule:: timetracker.loggers
   :members:

timetracker.utils.writers
-------------------------

.. automodule:: timetracker.utils.writers
   :members:

.. _tracker:

Tracker
=======

timetracker.tracker.models
--------------------------

.. automodule:: timetracker.tracker.models
   :members:

timetracker.tracker.admin
-------------------------

.. automodule:: timetracker.tracker.admin
   :members:

timetracker.tracker.forms
-------------------------

.. automodule:: timetracker.tracker.forms
   :members:

timetracker.tracker.tests
-------------------------

.. automodule:: timetracker.tracker.tests
   :members:

.. _reporting:

Reporting
=========

timetracker.reporting.views
---------------------------

.. automodule:: timetracker.reporting.views
   :members:

timetracker.tracker.management.commands
---------------------------------------

CATW Report
-----------

.. automodule:: timetracker.tracker.management.commands.catw_report
   :members:

MEC OT Report
-------------
.. automodule:: timetracker.tracker.management.commands.mec_ot_report
   :members:

Holiday Chart
-------------

.. automodule:: timetracker.tracker.management.commands.holiday_chart
   :members:

Notify Overtime
---------------

.. automodule:: timetracker.tracker.management.commands.notifyovertime
   :members:

Send Weekly Reminders
---------------------

.. automodule:: timetracker.tracker.management.commands.send_weekly_reminders
   :members:

Test E-mails
------------

.. automodule:: timetracker.tracker.management.commands.testemails
   :members:
