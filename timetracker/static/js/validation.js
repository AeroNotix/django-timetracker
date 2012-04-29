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