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
        
    var text_information = "Start Time: " + full_st;
    var text_information = text_information + " | End Time: " + full_fi;
    var text_information = text_information + " | Breaks: " + breakLength_full;
    
    $("#day_information").fadeTo(500, 0, function() {    
        $("#day_information").text(text_information);
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
