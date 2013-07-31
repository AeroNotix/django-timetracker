TODO
====

* Get test coverage as high as possible.

COMPLETED GOALS
===============

* Refactor the user retrieval. This should be a method on the User class which gets all child objects.
  Similarly, this should automagically work for Administrators/Team Leaders/Users alike. This would
  simplify a great deal of requests and population of tables etc. fdbe32f21c3935dbf9189e3945bc1d3b850bce3c

* Benchmark the SQL queries. There are no problems with them at the moment but I'd like to see if they
  are as optimal as they can be.

* Write more tests for the new features:

   - Enable/Disable users.
   - YearView

* Look into adding reporting functionality.
