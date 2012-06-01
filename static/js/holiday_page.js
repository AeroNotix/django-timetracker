var mouseState = false;
document.onmousedown = function(e){
    mouseState = true;
}
document.onmouseup = function(e){
    mouseState = false;
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

    $("#holiday-table")
        .find(".job_code").each( function () {
            if ( $("#is_team_leader").attr("value") ) {
                $(this).text('');
            }
        });

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
    $("#employees-select, #day_options").change(function () {
        retrieveComments();
    });
    $("#year_select, #month_select").change(function () {
        change_table_data();
    });

    $("#holiday-table")
        .attr("border", "1")

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

    $.ajax({
        type: "GET",
        dataType: "HTML",
        url: "/holiday_planning/" + year + "/" + month,
        success: function(data) {

            $("#holiday-wrapper, #comments-wrapper").fadeTo(500, 0, function() {
                if ( $("#isie").attr("isie") === "true" ) {
                    $("#comments-wrapper").load(
                        "/holiday_planning/" + year + "/" + month + " #com-field"
                    );
                    $("#holiday-wrapper").load(
                        "/holiday_planning/" + year + "/" + month + " #holiday-table"
                    );
                } else {
                    var holiday_html = $(data).find("#holiday-wrapper").html();
                    var comments_html = $(data).find("#comments-wrapper").html();
                    var table_year = $(data).find("#holiday-table").attr("year");
                    var table_month = $(data).find("#holiday-table").attr("month");

                    $("#com-field").html(comments_html);
                    $("#holiday-table").html(holiday_html);
                }
                $("#holiday-table").attr("year", table_year);
                $("#holiday-table").attr("month", table_month);
                addFunctions();
                $("#year_select").val(year);
                $("#month_select").val(month);
                $("#holiday-wrapper, #comments-wrapper").fadeTo(500, 1);
            });
            checkTeamLeader();
        }
    });
    return true;
}

function removeComment() {
    "use strict";

    /*
      Function which removes a comment from the database for a specific
      tracking entry.
    */

    $.ajaxSetup({
        type: "POST",
        dataType: "json"
    });

    $.ajax({
        url: '/ajax/',
        data: {
            form_type: 'remove_comment',
            year: $("#holiday-table").attr("year"),
            month: $("#holiday-table").attr("month"),
            user: $("#employees-select").val(),
            day: $("#day_options").val()
        },
        success: function (data) {
            if (data.success) {
                retrieveComments();
                change_table_data();
            } else {
                alert(data.error)
            }
        },
        error: function (data) {
            alert(data.error);
        }
    });

}

function insertComment() {

    "use strict";

    /*
      Function which inserts a comment into the database for a specific
      tracking entry.
    */

    $.ajaxSetup({
        type: "POST",
        dataType: "json"
    });

    $.ajax({
        url: '/ajax/',
        data: {
            form_type: 'add_comment',
            year: $("#holiday-table").attr("year"),
            month: $("#holiday-table").attr("month"),
            user: $("#employees-select").val(),
            day: $("#day_options").val(),
            comment: $("#comments-field-comment").val()
        },
        success: function (data) {
            if (data.success) {
                retrieveComments();
                change_table_data();
            } else {
                alert(data.error)
            }
        },
        error: function (data) {
            alert(data.error);
        }
    });

}

function retrieveComments() {

    "use strict";

    /*
      Function which retrieves the comment associated with a tracking entry,
      this allows managers to apply a comment onto a field and edit the
      comments that they have already added onto a field by selecting the
      dates that they used it on.
    */

    $.ajaxSetup({
        type: "GET",
        dataType: "json"
    });

    $("#comments-field-comment").val('');

    $.ajax({
        url: '/ajax/',
        data: {
            form_type: 'get_comments',
            year: $("#holiday-table").attr("year"),
            month: $("#holiday-table").attr("month"),
            user: $("#employees-select").val(),
            day: $("#day_options").val()
        },
        success: function (data) {
            if (data.success) {
                $("#comments-field-comment").val(data.comment);
            } else {
                alert(data.error)
            }
        },
        error: function(data) {
            alert(data.error);
        }
    });

    return true;

}

function checkTeamLeader() {

    /*
      Function which checks if the user is a team leader.

      If so, the field is removed
    */

    "use strict";

    var is_team_leader = $("#is_team_leader").attr("value");

    $("#holiday-table")
        .find(".job_code").each( function () {
            if ( is_team_leader ) {
                $(this).text('');
            }
            $(this).css("color", "black")
        });

    return true;
}

$(function () {
    addFunctions();
    checkTeamLeader();
});