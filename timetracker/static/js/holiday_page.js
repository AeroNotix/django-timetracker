
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
}

function submit_all() {
    
    /* 
       Submits all entries on the form
    */

    $("#holiday-table")
        .find(":button")
        .not("#submit_all")
        .each(function () {
            $(this).trigger("click");
        });
}

function submit_holidays(user_id) {
    /*
       En masse changes a set of holidays and
       takes a user_id as a parameter and returns
       undefined.
    */
    
    // create a map to hold the holidays
    var holiday_map = JSON;

    // iterate through the table and check if it's
    // selected or not, if it's selected, ignore it.
    // else, add the number and the class to the map.
    $("#holiday-table")
        .find("td[usrid='"+user_id+"']")
        .each(function () {
            // get the bg colour of the td
            var current_class = $(this).attr('class');
            if (current_class !== "selected") {
                holiday_map[$(this).text()] = current_class;
            }
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

function addFunctions () {

    "use strict";

    // all the daytype classes
    // are assigned a click handler which
    // swaps the colour depending on what
    // it currently is.
    $("#holiday-table")
        .find('.empty, .WKDAY, .SICKD, .HOLIS, .SPECI, .MEDIC, .PUABS, .PUWRK, .SATUR, .RETRN, .WKHOM, .OTHER')
        .not(":button")
        .mouseover(function (e) {
            if (mouseState) {

                if ($(this).hasClass("selected")) {
                    $(this).removeClass("selected");
                } else {
                    $(this).removeClass();
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
                $(this).removeClass();
                $(this).addClass("selected");
            }
        });

    $("#holiday-table")
        .find(".user-td")
        .attr("width", "200")

}

$(function () {
    addFunctions();
});

