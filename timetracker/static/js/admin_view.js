/* 
   Functions to deal with the client-side
   actions of the administrator view
*/

function onOptionChange(date) {

    /*
      Function triggers the change in the
      calendar on the template to show the
      calendar body
    */

    $.ajaxSetup({type: 'POST'});

    var eeid = $("#user_select").val();

    $.ajax({
        url: "/ajax/",
        dataType: 'json',
        data: {
            'form_type': 'admin_get',
            'eeid': eeid
        },
        success: function (data) {
            $("#calendar_div").html(data.calendar);
            $("#calendar tr td a").attr("href", "#");
            $("#calendar tr td a").css({'color':'black'});
        }
    });
    return true;
}

function toggleChangeEntries(st_hour, st_min, full_st,
                             fi_hour, fi_min, full_fi,
                             entry_date, daytype,
                             change_id, breakLength,
                             breakLength_full) {

    "use strict";

    var start_string = "Start Time: "+full_st;
    var end_string = " | End Time: "+full_fi;
    
    function pad(str, length, chr) {
        str = '' + str;
        if (str.length < length) {
            var pad_string = '';
            while ((pad_string+str).length < (length)) {
                pad_string = chr+pad_string;
            }
            str = pad_string+str;
        }
        return str;
    }

    /*
       Here we are building the time string from the start time,
       the end time and the break time.

       What we do is minus the start time from the end time,
       then minus the break time in minutes from 60, then
       concatenate them all together. This will break if the
       break time needs to go above 60 minutes.
    */

    var break_time = 60 - breakLength;
    if (break_time < 60) {
        var breaks = pad(60 - breakLength, 2, "0");
        var hour_string = pad((fi_hour - st_hour) - 1, 2, "0");
    } else {
        var breaks = "00";
        var hour_string = pad(fi_hour - st_hour, 2, "0");
    }
    
    var shiftLength = " | Shift Length: " + hour_string + ":" + breaks;

    var text_information = start_string+end_string;
    $("#day_information").fadeTo(500, 0, function() {    
        $("#day_information").text(text_information + shiftLength);
    });
    $("#day_information").fadeTo(500, 1);
}

function hideEntries() {
    $("#day_information").text('');
}

$(function () {
    $("#user_select").change(function () {
        onOptionChange();
    });
    onOptionChange();
});
