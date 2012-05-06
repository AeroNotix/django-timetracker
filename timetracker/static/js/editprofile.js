/*
   Module for client-side code for the user mode
   edit profile section
*/

function clearForm () {
    /*
       Clears the form
    */

    $("#id-password, #id-password-rpt")
        .each(function () {
            $(this).val('');
        });

    return true;
}


function submitChanges () {

    /*
      Gathers the form elements up
      and passes them to the ajax
      call which will change the
      data in the database
    */

    if (!confirm("Are you sure?")) {
        return false;
    }

    $.ajaxSetup({
        "type": "POST",
        "url": "/ajax",
        "dataType": "json"
    });

    var passwords = [
        $("#id-password").val(),
        $("#id-password-rpt").val()
    ]

    if (!checkStringLengths(passwords, 6)) {
        alert("Minimum length of passwords is 6");
        clearForm();
        return false;
    }

    if (!stringMatch("#id-password", "#id-password-rpt")) {
        alert("Passwords do not match");
        clearForm();
        return false;
    }

    var ajaxData = {
        "first_name": $("#id-first-name").val(),
        "last_name": $("#id-last-name").val(),
        "password": $("#id-password").val()
    }

    return true;
}