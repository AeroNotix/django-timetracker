function submit_holidays(user_id) {
    /*
       En masse changes a set of holidays and
       takes a user_id as a parameter and returns
       undefined.
    */

    // create an array to hold the holidays
    var additional_holidays = new Array();
    $("#holiday-table")
        .find("td[usrid='"+user_id+"']")
        .each(function () {
            // get the bg colour of the td
            var current_colour = $(this).css('backgroundColor');

            // if the cell is purple, it means it's highlighted,
            // that means we need to assign the holiday in the
            // database
            if (current_colour === 'rgb(85, 26, 123)') {
                additional_holidays.push($(this).text());
            }
        });

    // no point making an ajax call if we've got
    // no data
    if (!additional_holidays.length > 0) {
        return
    }

    alert(additional_holidays);
    // setup our ajax properties
    $.ajaxSetup({
        type: 'POST',
        dataType: 'json',
    });

    // make the ajax call
    $.ajax({
        url: '/ajax/',
        data: {
            'form_type': 'mass_holidays',
            'year': $("#holiday-table").attr("year"), // from the table header
            'month': $("#holiday-table").attr("month"),
            'days': String(additional_holidays),
            'user_id': user_id
        },
        success: function(data) {
            if (data.success === true) {
                alert("Holidays updated successfully");
            } else {
                alert(data.error)
            }
        },
        error: function(ajaxObj, textStatus, error) {
            alert(error);
        }
    });

}

$(function () {

    "use strict";

    $("#holiday-table")
        .attr("border", "1")
        .find("td")
        .attr("width", "18")
        .attr("height", "18");


    // all 'holis' and 'empty' classes
    // are assigned a click handler which
    // swaps the colour depending on what
    // it currently is.
    $("#holiday-table")
        .find(".HOLIS, .empty")
        .not(":button")
        .click(function() {

            // get the current colours
            var current_colour = $(this).css('backgroundColor');

            // make a map of what the current colour
            // changes to when the table data is
            // clicked.
            var colour_map = {
                'rgb(85, 26, 123)': 'rgb(0, 0, 0)',
                'rgb(0, 0, 0)': 'rgb(85, 26, 123)'
            }

            $(this).css({
                'backgroundColor': colour_map[current_colour]
            });

        });

    $("#holiday-table")
        .find(".user-td")
        .attr("width", "200")

});
