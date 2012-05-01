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

$(function () {
    $("#user_select").change(function () {
        onOptionChange();
    });
    onOptionChange();
});