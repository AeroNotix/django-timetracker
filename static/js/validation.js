/*
  Intended to validate form fields
*/

function validateDate (field) {

    /*

       Validates a field against the following:-

       \d{4} = four digits
       \- = literal minus
       d{1,2} = one or two digits

       Takes a field element as a parameter and
       returns true for a match, false for not

    */

    return /\d{4}\-\d{1,2}\-\d{1,2}/g.test($(field).val());
}

function validateTimePair(fieldA, fieldB) {
    /*
       Validates two time fields against each other.
    */
    var fieldA_matches = $(fieldA).val().split( /\:/ );
    var fieldB_matches = $(fieldB).val().split( /\:/ );

    function verifyAll(match_group) {
        /*
           Validates that the group matches are both
           valid time portions.

           i.e. 04 or 12.
        */
        for (idx in match_group) {
            if (!match_group[idx].match( /\d{1,2}/ )) {
                return false;
            }
        }
        return true;
    }

    if (!verifyAll(fieldA_matches) && !verifyAll(fieldB_matches)) {
        return false;
    }

    var min_diff = fieldB_matches[1] - fieldA_matches[1];
    var hour_diff = fieldB_matches[0] - fieldA_matches[0];

    if (min_diff < 0) {
        min_diff = min_diff + 60;
        hour_diff--;
    }

    if (hour_diff < 0) {
        return false;
    } else {
        return true;
    }
}

function validateTime (field) {

    /*

       Validates a field against the following:-

       \d{1,2} = two digits
       \: = literal colon
       \d{1,2} = two digits
       \d{1,2}? = two optional digits

       Takes a field element as a parameter and
       returns true for a match, false for not

    */

    return /\d{1,2}\:\d{1,2}(\:\d{1,2})?/g.test($(field).val());
}

function stringMatch (fieldA, fieldB) {

    /*
       String matching function
    */

    return $(fieldA).val() === $(fieldB).val();
}

function checkStringLengths (stringArray, len) {
    /*
      Checks all strings in the array for
      a given length

      Takes an array of strings and an integer
      return true if all strings validate,
      false otherwise.
    */

    for (idx=0;idx<stringArray.length;idx++) {
        if (stringArray[idx].length < len) {
            return false;
        }
    }
    return true;
}

function emailValidate (element_name) {
    /*
       Validates an email address

       Takes a element tag and returns boolean if the
       value matches or not.
    */

    var email = $(element_name).val();

    /*
      [A-Za-z0-9_.\-]+ = matches all alphanumeric characters with -, _ and .
      @ = matches @
      \.[A-Za-z]+ = matches . with any length alphanumeric string after
    */
    return /^[A-Za-z0-9_.\-]+@[A-Za-z0-9_.\-]+\.[A-Za-z]+$/g.test(email);
}
