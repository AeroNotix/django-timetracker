"""
Database errors give out a tuple of information. The first of which is a
number, we can grab that and check what kind of error we're getting

Currently this is somewhat small as there aren't many errors that get thrown
consistantly to warrant putting their codes into a module.

:attr:`DUPLICATE_ENTRY`: This is thrown when the database validation reports
that there is already an entry in the database with conflicting values for
whatever is set as a Unique and/or UniqueTogether.

:attr:`CONNECTION_REFUSED`: This error is thrown when the SMTP server is down
and/or is not responding.
"""

DUPLICATE_ENTRY = 1062
CONNECTION_REFUSED = 111
