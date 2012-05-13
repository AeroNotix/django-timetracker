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

    if ( $(field).val().match( /\d{4}\-\d{1,2}\-\d{1,2}/ ) ) {
        return true;
    } else {
        return false;
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

    if ( $(field).val().match( /\d{1,2}\:\d{1,2}(\:\d{1,2})?/ ) ) {
        return true;
    } else {
        return false;
    }
}

function stringMatch (fieldA, fieldB) {

    /*
       String matching function
    */

    if ($(fieldA).val() === $(fieldB).val()) {
        return true;
    } else {
        return false;
    }
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
    */

    var email = $(element_name).val();

    /*
      [A-Za-z0-9_.]+ = matches all alphanumeric characters with _ and .
      @ = matches @
      \.[A-Za-z]+ = matches . with any length alphanumeric string after
    */
    if (email.match( /^[A-Za-z0-9_.]+@[A-Za-z0-9_.]+\.[A-Za-z]+$/ ) ) {
        return true;
    } else {
        return false;
    }
}