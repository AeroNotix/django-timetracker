function onOptionChange() {
    /* 
       When the select box is changed the form needs to 
       be updated with the employees data, so we grab the
       value and make an ajax request to the database to
       pull the data

       Returns undefined and takes no parameters
    */
    "use strict";

    var user_id = $("#user_select").val();
    if (user_id === 'null') {
        clearForm()
        return
    }

    $.ajaxSetup({type: 'POST'});

    $.ajax({
        url: '/ajax/',
        dataType: "json",
        data: {
            'user_id': user_id,
            'form_type': 'get_user_data'
        },

        success: function (data) {
            if (data.success === true) {
                $("#id_breaklength").timepicker("destroy");
                $("#id_shiftlength").timepicker("destroy");
                
                setupUI();

                $("#id_user_id").val(data.username);
                $("#id_firstname").val(data.firstname);
                $("#id_lastname").val(data.lastname);
                $("#id_user_type").val(data.user_type);
                $("#id_market").val(data.market);
                $("#id_process").val(data.process);
                $("#id_start_date").val(data.start_date);
                $("#id_breaklength").val(data.breaklength);
                $("#id_shiftlength").val(data.shiftlength);
            } else {
                alert(data.error);
            }
        }
    });
}

function clearForm() {

    /*
       Clears the entire form

       Takes no parameters and gives no fucks
    */

    "use strict";

    $("#user-edit-form")
        .find(":input")
        .not(":button")
        .each( function () {
            $(this).val('');
        }
    );
}

function deleteEntry() {

    /* 
       Asynchrously deletes an entry
       
       Takes no parameters and returns undefined
    */

    var user_id = $("#user_select").val();
    if (user_id === 'null') {
        return 
    }

    if (!confirm("Are you sure?")) {
        return false;
    }

    $.ajaxSetup({
        type: "POST",
        dataType: "json"
    });

    $.ajax({
        url: '/ajax/',
        data: {
            'user_id': user_id,
            'form_type': 'delete_user'
        },
        success: function(data) {
            if (data.success === true) {
                $("#edit-user-wrapper").load(
                    "/user_edit/ #edit-user-table",
                    function () {
                        ajaxSuccess();
                    }
                );
            } else {
                alert(data.error);
            }
        }
    });
}

       
function addEntry() {

    /* 
       Asynchrnously adds a user
       
       Takes no parameters and returns undefined
    */

    if (!confirm("Are you sure?")) {
        return false;
    }

    $.ajaxSetup({
        type: "POST",
        dataType: "json"
    });

    var data = [
        'user_id',
        'firstname',
        'lastname',
        'user_type',
        'market',
        'process',
        'start_date',
        'breaklength',
        'shiftlength',
    ]

    var form_data = {'form_type': 'add_user'};
    var index = 0;
    // loop through the wrapped set which is the same,
    // size as the data array, that way we can get the 
    // vals easy
    $("#user-edit-form").find(":input").not(":button").each(
        function () {
            form_data[data[index]] = $(this).val();
            index++
        }
    );

    $.ajax({
        url: '/ajax/',
        data: form_data,
        success: function (data) {
            if (data.success === true) {
                $("#edit-user-wrapper")
                    .load("/user_edit/ #edit-user-table",
                          function() {
                              $("#user_select").change(function() {
                                  onOptionChange();
                              });
                              ajaxSuccess();
                          });
            } else {
                alert(data.error);
            }
        }
    });
}

function setupUI() {
    "use strict";

    $("#id_start_date").datepicker().val('');
    $("#id_start_date").datepicker("option", "dateFormat", 'yy-mm-dd');
    $("#id_breaklength").timepicker({
        showHour: false,
        timeFormat: 'hh:mm:ss'
    });
    $("#id_shiftlength").timepicker({
        timeFormat: 'hh:mm:ss'
    });
}

function ajaxSuccess() {

    /* 
       Lazy method for ajaxSuccess
    */
    
    "use strict";

    setupUI();
    clearForm();
    $("#user_select").val("null");
    $("#user_select").change(function() {
        onOptionChange();
    });


    // The form is automatically generated from the
    // model, this means that it's got some fields
    // that we don't want to show. We remove the
    // password field and the label associated with it.
    $("#user-edit-form")
        .find("label")
        .each( function () {
            if ($(this).attr("for") === "id_password") {
                $(this).remove();
                $("#id_password").remove();
            }
        });
}

$(function () {
    "use strict";
    ajaxSuccess();
});