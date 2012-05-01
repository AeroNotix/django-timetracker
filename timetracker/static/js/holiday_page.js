var mouseState = false;
document.onmousedown = function(e){
    mouseState = true;
}
document.onmouseup = function(e){
    mouseState = false;

    // In IE obviously we use a different function
    //
    // this will deselect the text after dragging
    // has finished.
    if (document.selection) {
        document.selection.empty()
    } else {
        window.getSelection().removeAllRanges()
    }

}

function applyClass(klass) {

    /*
       Checks all the table elements,
       if they are selected, it removes the
       selected class (and all other classes)
       and applies the passed in class
    */

    $("#holiday-table")
        .find("td")
        .each(function () {
            if ($(this).hasClass("selected")) {
                $(this).removeClass();
                $(this).addClass(klass);

            }
        });
    return true;
}

function submit_all() {

    /*
       Submits all entries on the form

       Takes no parameters and returns true/false
       depending on success.
    */

    var successfully_completed = false;
    $("#holiday-table")
        .find(":button")
        .not("#submit_all, #btn_change_td")
        .each(function () {
            var call = submit_holidays($(this).attr("user_id"), true)
            if (call === true) {
                successfully_completed = true;
            } else {
                successfully_completed = false;
            }
        });
    // refresh the table data
    setTimeout("change_table_data()", 1000);

    // if (successfully_completed) {
    //     alert("Holidays change successfully!");
    // } else {
    //     alert("There was an error adding holidays");
    // }

    return successfully_completed;
}

function submit_holidays(user_id, mass) {
    /*
       En masse changes a set of holidays and
       takes a user_id as a parameter.

       Mass is true/false, if true it

       Returns true for success, false for error
    */

    if (!user_id) {
        return true;
    }

    // create a map to hold the holidays
    var holiday_map = JSON;

    // iterate through the table and check if it's
    // selected or not, if it's selected, ignore it.
    // else, add the number and the class to the map.
    $("#holiday-table")
        .find("td[usrid='"+user_id+"']")
        .each(function () {
            // remove the selected class off the element
            $(this).removeClass("selected");
            // get the bg colour of the td
            var current_class = $(this).attr('class');
            // this check is redundant but it helps if there
            // are any changed to the selection methods
            if (current_class !== "selected") {
                holiday_map[$(this).text()] = current_class;
            }
        });

    // setup our ajax properties
    $.ajaxSetup({
        type: 'POST',
        dataType: 'json'
    });

    $.ajax({
        url: '/ajax/',
        data: {
            'form_type': 'mass_holidays',
            'year': $("#holiday-table").attr("year"), // from the table header
            'month': $("#holiday-table").attr("month"),
            'holiday_data': JSON.stringify(holiday_map),
            'user_id': user_id
        },
        success: function(data) {
            if (data.success === true) {
                if (!mass) {
                    alert("Holidays updated successfully");
                }
            } else {
                alert(data.error);
            }
        },
        error: function(ajaxObj, textStatus, error) {
            alert(error);
        }
    });

    // return true so programmatic callers can
    // see we've completed
    return true;
}

function addFunctions () {

    "use strict";

    // all the daytype classes
    // are assigned a click handler which
    // swaps the colour depending on what
    // it currently is.
    $("#holiday-table")
        .find('.empty, .DAYOD, .TRAIN, '
            + '.WKDAY, .SICKD, .HOLIS, '
            + '.SPECI, .MEDIC, .PUABS, '
            + '.PUWRK, .SATUR, .RETRN, '
            + '.WKHOM, .OTHER')
        .not(":button")
        .attr("unselectable", "on")   // make it so you can't select text
        .mouseover(function (e) {
            if (mouseState) {

                if ($(this).hasClass("selected")) {
                    $(this).removeClass("selected");
                } else {
                    $(this).addClass("selected");
                }
                e.preventDefault();
                e.stopPropagation();
            }
        })
        .mousedown(function (e) {
            if ($(this).hasClass("selected")) {
                $(this).removeClass("selected");
            } else {
                $(this).addClass("selected");
            }
        });

    $("#year_select").val($("#holiday-table").attr("year"));
    $("#month_select").val($("#holiday-table").attr("month"));
    $("#year_select, #month_select").change(function () {
        change_table_data();
    });

    $("#holiday-table")
        .attr("border", "1")
        .find(".user-td")
    return true;
}

function change_table_data () {

    "use strict";

    /*
       Function which takes the values of the select boxes
       constructs an ajax call based on those and replaces
       the table with the data returned from the ajax call
    */

    var year = $("#year_select").val();
    var month = $("#month_select").val();
    $("#holiday-wrapper").fadeTo(500, 0, function() {
        $("#holiday-wrapper").load(
            "/holiday_planning/" + year + "/" + month + " #holiday-table",
            function () {
                $("#holiday-wrapper").fadeTo(500, 1);
                addFunctions();
            });
    });
    return true;
}

$(function () {
    addFunctions();
    change_table_data();
});