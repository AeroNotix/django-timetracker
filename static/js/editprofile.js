/*global $,confirm,checkStringLengths,alert,stringMatch*/
/*
   Module for client-side code for the user mode
   edit profile section
*/

function clearForm() {
	"use strict";
    /*
       Clears the form
    */

    $("#id-password, #id-password-rpt")
        .each(function () {
            $(this).val('');
        });

    return true;
}


function submitChanges() {
	"use strict";
    /*
      Gathers the form elements up
      and passes them to the ajax
      call which will change the
      data in the database
    */

	var passwords = [],
	    ajaxData = {};

    if (!confirm("Are you sure?")) {
        return false;
    }

	passwords = [
        $("#id-password").val(),
        $("#id-password-rpt").val()
    ];

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

    ajaxData = {
        "first_name": $("#id-first-name").val(),
        "last_name": $("#id-last-name").val(),
        "password": $("#id-password").val()
    };

    $.ajaxSetup({
        type: "POST"
    });

    $.ajax({
        url: "/ajax/",
        dataType: "json",
        data: {
            "form_type": "profileedit",
            "firstname": $("#id-firstname").val(),
            "lastname": $("#id-lastname").val(),
            "password": $("#id-password").val()
        },
        success: function (data) {
            $("#edit-profile-wrapper")
                .fadeTo(500, 0, function () {
                    $("#edit-profile-wrapper")
                        .load("/edit_profile/ #edit-profile-table",
                              function () {
                                $("#edit-profile-wrapper")
                                      .fadeTo(500, 1);
                            });
                });
        }
    });
    return true;
}
