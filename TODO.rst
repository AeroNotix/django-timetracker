TODO
====

* Refactor the user retrieval. This should be a method on the User class which gets all child objects.
  Similarly, this should automagically work for Administrators/Team Leaders/Users alike. This would
  simplify a great deal of requests and population of tables etc.

* Benchmark the SQL queries. There are no problems with them at the moment but I'd like to see if they
  are as optimal as they can be.

* Write more tests for the new features:

   - Enable/Disable users.
   - YearView
   - Anything else since commit 76cf2d3bd343158c5aa20017047ab5edab367487

* Look into adding reporting functionality.
