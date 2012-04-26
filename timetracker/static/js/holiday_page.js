function submit_holidays(user_id) {
    /*
       En masse changes a set of holidays and
       takes a user_id as a parameter and returns
       undefined.
    */
    
    // create a map to hold the holidays
    var holiday_map = JSON;
    $("#holiday-table")
        .find("td[usrid='"+user_id+"']")
        .each(function () {
            // get the bg colour of the td
            var current_class = $(this).attr('class');
            holiday_map[$(this).text()] = current_class;
        });

    // setup our ajax properties
    $.ajaxSetup({
        type: 'POST',
        dataType: 'json'
    });
    
    // make the ajax call
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
                alert("Holidays updated successfully");
            } else {
                alert(data.error);
            }
        },
        error: function(ajaxObj, textStatus, error) {
            console.log(error);
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
        .find('.empty, .WKDAY, .SICKD, .HOLIS, .SPECI, .MEDIC, .PUABS, .PUWRK, .SATUR, .RETRN, .WKHOM, .OTHER')
        .not(":button")
        .click(function() {
            // get the current colours
            var current_class = $(this).attr('class');
            // make a map of what the current colour
            // changes to when the table data is
            // clicked.
            var colour_class_map = {
                'empty': 'WKDAY',
                'WKDAY': 'SICKD',
                'SICKD': 'HOLIS',
                'HOLIS': 'SPECI',
                'SPECI': 'MEDIC',
                'MEDIC': 'PUABS',
                'PUABS': 'PUWRK',
                'PUWRK': 'SATUR',
                'SATUR': 'RETRN',
                'RETRN': 'WKHOM',
                'WKHOM': 'OTHER',
                'OTHER': 'empty'
            }
            
            // set it to the colour we found
            $(this).attr("class", colour_class_map[current_class]);

        });

    $("#holiday-table")
        .find(".user-td")
        .attr("width", "200")

});







