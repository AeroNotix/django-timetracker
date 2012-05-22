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

    console.log("Full Start: " + full_st);
    console.log("Full End: " + full_fi);
    console.log("Breaks: " + breakLength_full);
    

    var working_hours = (fi_hour - st_hour) * 3600;
    var working_mins = ((fi_min - st_min) / 60) * 3600;
    var working_seconds = working_hours + working_mins;
    var time_hours = parseInt((working_seconds / 3600));
    var time_minutes = parseInt(((60 * ((working_seconds / 3600.0) % 1))));
    console.log(time_hours+':'+time_minutes);
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
